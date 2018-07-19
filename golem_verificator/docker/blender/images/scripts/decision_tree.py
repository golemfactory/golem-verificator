import numpy as np

from sklearn import tree
from sklearn.externals import joblib
from sklearn.externals.six import StringIO
import pydot

## ======================= ##
##
class DecisionTree:
    
    ## ======================= ##
    ##
    def __init__( self, clf ):
        self.clf = clf
        
    ## ======================= ##
    ##
    @staticmethod
    def load( file ):
    
        data = joblib.load( file )
        tree = DecisionTree( data[0] )
        tree.set_features_labels(data[1])
        return tree, data[1]

    ## ======================= ##
    ##
    def set_features_labels( self, labels ):
    
        self.features_labels = labels
            
    ## ======================= ##
    ##
    @staticmethod
    def compute_unique_labels( class_labels ):

        unique_labels = set( class_labels )
        
        labels_list = list( unique_labels )
        labels_list.sort()
        
        labels_list = [ label.decode('UTF-8') for label in labels_list ]
        
        return labels_list
        
    ## ======================= ##
    ##
    def save_graph( self, file ):
        
        print( "Saving tree to file [" + file + "]" )
        
        dot_data = StringIO() 
        tree.export_graphviz( self.clf, out_file=dot_data, feature_names = self.features_labels, rounded = True, filled = True, class_names = self.labels ) 
        
        graph = pydot.graph_from_dot_data( dot_data.getvalue() )
        graph[ 0 ].write_pdf( file ) 
        
        
    ## ======================= ##
    ##
    @staticmethod
    def train( samples, class_labels, params ):

        print( "Teaching decision tree." )
        clf = tree.DecisionTreeClassifier()
        clf.max_depth = params.max_depth
        clf.class_weight = params.classes_weights
        clf.criterion = params.criterion
        clf.min_samples_leaf = params.min_samples_leaf
        clf.min_impurity_decrease = params.min_impurity_decrease
        
        clf = clf.fit( samples, class_labels )
        
        return clf

    ## ======================= ##
    ##
    @staticmethod
    def extract_features( data, labels ):
    
        print( "Extracting features from dataset." )
        samples = data[ labels ]
        return samples.view( np.float64 ).reshape( samples.shape + (-1,) )
        
    ## ======================= ##
    ##
    @staticmethod
    def train_and_save( data, class_label, features_labels, params, file ):
        
        samples = DecisionTree.extract_features( data, features_labels )
        class_labels = data[ class_label ]
        
        clf = DecisionTree.train( samples, class_labels, params )
        
        print( "Saving tree to file: " + file )
        joblib.dump( [clf, features_labels], file )
        
        decision_tree = DecisionTree( clf )
        decision_tree.set_features_labels( features_labels )
        decision_tree.labels = DecisionTree.compute_unique_labels( class_labels )
        
        return decision_tree
        
        
    ## ======================= ##
    ##
    def classify( self, data_set ):
        
        samples = data_set[ self.features_labels ]
        samples = samples.view( np.float64 ).reshape( samples.shape + (-1,) )
        
        results = self.clf.predict( samples )
        
        return np.array( results )

    def classify_with_feature_vector(self, feature_vector, labels):

        numpy_format = []
        for label in labels:
            numpy_format.append((label, np.float64))
        
        converted_features = np.zeros(1, dtype=numpy_format)
        for name in converted_features.dtype.names:
            converted_features[name] = feature_vector[name]

        samples = converted_features.view(np.float64).reshape(
            converted_features.shape + (-1,))

        results = self.clf.predict(samples)

        return np.array(results)
        
        
        