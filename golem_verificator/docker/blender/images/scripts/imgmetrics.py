import io
import os
import json
import pickle
from . import metrics

class ImgMetrics:
    """
    ImgMetrics is a structure for storing img comparison metric.
    methods write/load are to facilitate file movement to/from docker.
    """

    def __init__(self, dictionary=None):
        self.ssim = None
        self.reference_variance = None
        self.image_variance = None
        self.ref_edge_factor = None
        self.comp_edge_factor = None
        self.edge_difference = None
        self.wavelet_low = None
        self.wavelet_mid = None
        self.wavelet_high = None
        self.histograms_correlation = None
        self.max_x_mass_center_distance = None
        self.max_y_mass_center_distance = None
        self.crop_resolution = None

        # ensure that the keys are correct
        keys = ImgMetrics.get_metric_names()
        keys.append('Label')

        for key in keys:
            if key not in dictionary:
                raise KeyError("missing metric:" + key)

        # read into ImgMetrics object
        for key in dictionary:
            setattr(self, key, dictionary[key])

    @staticmethod
    def get_metric_classes():
        available_metrics = [metrics.ssim.MetricSSIM,
                metrics.psnr.MetricPSNR,
                metrics.variance.ImageVariance,
                metrics.edges.MetricEdgeFactor,
                metrics.wavelet.MetricWavelet,
                metrics.histograms_correlation.MetricHistogramsCorrelation,
                metrics.mass_center_distance.MetricMassCenterDistance]
        
        return available_metrics


    @staticmethod
    def get_metric_names():
        metric_names = []
        for metric_class in ImgMetrics.get_metric_classes():
            metric_names = metric_names + metric_class.get_labels()
        return metric_names

    def to_json(self):
        str_ = json.dumps(self,
                          default=lambda o: o.__dict__,
                          indent=4,
                          sort_keys=True,
                          separators=(',', ': '),
                          ensure_ascii=False)
        return str_


    def write_to_file(self, file_name='img_metrics.txt'):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, file_name)

        data = self.to_json()
        with io.open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

        return file_path

    @classmethod
    def load_from_file(cls, file_path=None):
        with open(file_path, 'r') as f:
            dictionary = json.load(f)
            img_metrics = cls(dictionary)
            return img_metrics
