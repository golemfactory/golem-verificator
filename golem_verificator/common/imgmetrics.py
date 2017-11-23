
import io
import json


class ImgMetrics:
    """
    ImgMetrics is a structure for storing img comparison metric.
    The file I/O utility is to facilitate file movement to/from docker.
    """

    def __init__(self, dictionary=None):
        self.imgCorr = None  # for intellisense
        self.SSIM_normal = None
        self.MSE_normal = None
        self.SSIM_canny = None
        self.SSIM_wavelet = None
        self.MSE_wavelet = None

        # ensure that the keys are correct
        keys = ['imgCorr', 'SSIM_normal', 'MSE_normal', 'SSIM_canny',
                'SSIM_wavelet', 'MSE_wavelet']

        for key in keys:
            if key not in dictionary:
                raise Exception("missing metric:" + key)

        # read into ImgMetrics object
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def to_json(self):
        str_ = json.dumps(self,
                          default=lambda o: o.__dict__,
                          indent=4,
                          sort_keys=True,
                          separators=(',', ': '),
                          ensure_ascii=False)
        return str_

    def write_to_file(self, file_path='data.txt'):
        data = self.to_json()
        with io.open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

    @classmethod
    def load_from_file(cls, file_path='data.txt'):
        if file_path:
            with open(file_path, 'r') as f:
                dictionary = json.load(f)
                img_metrics = cls(dictionary)
                return img_metrics
