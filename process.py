"""
process.py — Xử lý 8 ảnh đã chụp, tính phase map và defect (curvature) map.

Phương pháp:
- 4-step phase shifting: phi = atan2(I3 - I1, I0 - I2)
- Modulation amplitude = sqrt((I3-I1)^2 + (I0-I2)^2) / 2  → mask vùng tin cậy
- Slope = gradient không gian của phase, dùng trick complex-exponential để
  tránh ảnh hưởng của 2π wraparound (KHÔNG cần phase unwrap).
- Curvature = đạo hàm của slope. Đây là MAP DEFECT chính: defect cục bộ
  (vết móp, bụi, scratch, orange peel) cho spike rõ ràng trên curvature map.
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CAPTURE_DIR = Path("captures")


def load_gray(name):
    path = CAPTURE_DIR / f"{name}.png"
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Thieu {path} — chay capture.py truoc")
    return img.astype(np.float32)


def phase_4step(images):
    """4-step phase shifting algorithm.
    images = [I_0, I_90, I_180, I_270] tương ứng với 4 phase shifts 0, π/2, π, 3π/2.
    Trả về (wrapped_phase, modulation_amplitude).
    """
    num = images[3] - images[1]   # 2*B*sin(phi)
    den = images[0] - images[2]   # 2*B*cos(phi)
    phi = np.arctan2(num, den)
    modulation = 0.5 * np.sqrt(num * num + den * den)
    return phi, modulation


def wrap_safe_gradient(phi, axis):
    """Gradient của phase, tránh nhảy 2π bằng trick complex exponential.
    d(phi)/d(axis) ≈ angle( exp(i*phi[next]) * conj(exp(i*phi[prev])) )
    """
    c = np.exp(1j * phi)
    if axis == 0:  # gradient theo y
        diff = c[1:, :] * np.conj(c[:-1, :])
        grad = np.angle(diff)
        grad = np.vstack([grad, grad[-1:, :]])  # pad cho cùng kích thước
    elif axis == 1:  # gradient theo x
        diff = c[:, 1:] * np.conj(c[:, :-1])
        grad = np.angle(diff)
        grad = np.hstack([grad, grad[:, -1:]])
    else:
        raise ValueError("axis phai la 0 hoac 1")
    return grad


def main():
    print("Loading captures...")
    Iv = [load_gray(f"V{i}") for i in range(4)]  # sọc dọc → mã hóa screen-x
    Ih = [load_gray(f"H{i}") for i in range(4)]  # sọc ngang → mã hóa screen-y

    print("Computing phase maps (4-step)...")
    phi_x, mod_x = phase_4step(Iv)
    phi_y, mod_y = phase_4step(Ih)

    # Modulation thấp = vùng không phản xạ pattern rõ (mép, nền, vùng tối).
    modulation = np.minimum(mod_x, mod_y)
    # Mask: chỉ giữ vùng có signal đủ mạnh
    thr = max(5.0, 0.15 * modulation.max())
    mask = (modulation > thr).astype(np.float32)
    # Làm mịn mask một chút để bớt nhiễu mép
    mask = cv2.GaussianBlur(mask, (5, 5), 1)
    mask = (mask > 0.5).astype(np.float32)

    print("Computing slope and curvature...")
    # Slope = gradient của phase. Đơn vị: rad/pixel.
    # phi_x mã hóa vị trí ngang trên màn hình → grad theo x trong ảnh = slope ngang bề mặt
    sx_x = wrap_safe_gradient(phi_x, axis=1)
    sx_y = wrap_safe_gradient(phi_x, axis=0)
    sy_x = wrap_safe_gradient(phi_y, axis=1)
    sy_y = wrap_safe_gradient(phi_y, axis=0)

    # Làm mịn slope trước khi đạo hàm lần 2 (giảm nhiễu)
    sx_x_s = cv2.GaussianBlur(sx_x, (5, 5), 1.2)
    sy_y_s = cv2.GaussianBlur(sy_y, (5, 5), 1.2)

    # Curvature: đạo hàm bậc 2 của phase = đạo hàm 1 của slope
    cxx = cv2.Sobel(sx_x_s, cv2.CV_32F, 1, 0, ksize=3)
    cyy = cv2.Sobel(sy_y_s, cv2.CV_32F, 0, 1, ksize=3)
    curvature = np.sqrt(cxx * cxx + cyy * cyy)
    curvature = cv2.GaussianBlur(curvature, (3, 3), 0.7)

    # Áp mask
    curvature_masked = curvature * mask
    slope_mag = np.sqrt(sx_x_s ** 2 + sy_y_s ** 2) * mask

    # Hiển thị
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))

    axes[0, 0].imshow(Iv[0], cmap='gray')
    axes[0, 0].set_title("Capture V0 (raw)")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(phi_x, cmap='hsv')
    axes[0, 1].set_title("Phase X (wrapped)")
    axes[0, 1].axis('off')

    axes[0, 2].imshow(phi_y, cmap='hsv')
    axes[0, 2].set_title("Phase Y (wrapped)")
    axes[0, 2].axis('off')

    axes[1, 0].imshow(modulation, cmap='viridis')
    axes[1, 0].set_title("Modulation (signal strength)")
    axes[1, 0].axis('off')

    axes[1, 1].imshow(slope_mag, cmap='magma')
    axes[1, 1].set_title("|Slope|  (do nghieng cuc bo)")
    axes[1, 1].axis('off')

    # Defect map — clip phần trăm cao để defect không bị "đè" bởi outlier
    vmax = np.percentile(curvature_masked[mask > 0], 99) if mask.sum() > 0 else 1.0
    axes[1, 2].imshow(curvature_masked, cmap='hot', vmax=vmax)
    axes[1, 2].set_title("DEFECT MAP (curvature) — sang = loi")
    axes[1, 2].axis('off')

    plt.tight_layout()
    out_path = "results.png"
    plt.savefig(out_path, dpi=120, bbox_inches='tight')
    print(f"Da luu {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
