import pprint

from imgs.imgrepr import load_img
from imgs.imgstats import ImgStatistics


def generate_stats(img_path1, img_path2):
    img1 = load_img(img_path1)
    img2 = load_img(img_path2)
    img_stats = ImgStatistics(img1, img2)
    stats = img_stats.get_stats()
    return {
        "ssim": stats[0],
        "mse": stats[1],
        "norm_mse": stats[2],
        "mse_bw": stats[3],
        "psnr": stats[4]
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage %s path_to_image1 path_to_image2" % sys.argv[0])
        sys.exit(-1)
    pprint.pprint(generate_stats(sys.argv[1], sys.argv[2]))
