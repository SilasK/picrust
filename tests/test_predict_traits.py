from math import e
from cogent.util.unit_test import main,TestCase
from numpy import array,array_equal,around
from cogent import LoadTree
from cogent.parse.tree import DndParser
from picrust.predict_traits  import assign_traits_to_tree,\
  predict_traits_from_ancestors, get_most_recent_ancestral_states,\
  fill_unknown_traits, linear_weight, make_neg_exponential_weight_fn,\
  weighted_average_tip_prediction

"""
Tests for predict_traits.py
"""

class TestPredictTraits(TestCase):
    """Tests of predict_traits.py"""

    def setUp(self):
        self.SimpleTree = \
          DndParser("((A:0.02,B:0.01)E:0.05,(C:0.01,D:0.01)F:0.05)root;")
    
        self.SimplePolytomyTree = \
          DndParser("((A:0.02,B:0.01,B_prime:0.03)E:0.05,(C:0.01,D:0.01)F:0.05)root;")
    
        self.SimpleTreeTraits =\
            {"A":[1.0,1.0],"E":[1.0,1.0],"F":[0.0,1.0],"D":[0.0,0.0]}
        
        self.PartialReconstructionTree =\
                DndParser("((((B:0.01,C:0.01)I3:0.01,A:0.01)I2:0.01,D:0.01)I1:0.01)root;")

        self.CloseToI3Tree =\
                DndParser("((((B:0.01,C:0.95)I3:0.01,A:0.01)I2:0.95,D:0.05)I1:0.95)root;")
        
        self.CloseToI1Tree =\
                DndParser("((((B:0.95,C:0.95)I3:0.95,A:0.01)I2:0.02,D:0.05)I1:0.05)root;")

        self.BetweenI3AndI1Tree=\
                DndParser("((((B:0.01,C:0.1)I3:0.02,A:0.01)I2:0.02,D:0.05)I1:0.02)root;")


        self.PartialReconstructionTraits =\
                {"B":[1.0,1.0],"C":[1.0,1.0],"I3":[1.0,1.0],"I1":[0.0,1.0],"D":[0.0,1.0]}

        self.GeneCountTraits =\
                {"B":[1.0,1.0],"C":[1.0,2.0],"I3":[1.0,1.0],"I1":[0.0,3.0],"D":[0.0,5.0]}
    
    def test_linear_weight(self):
        """linear_weight weights linearly"""
        
        max_d = 1.0
        d = 0.90
        obs = linear_weight(d,max_d)
        exp = 0.10
        self.assertFloatEqual(obs, exp)

        d = 0.0
        obs = linear_weight(d,max_d)
        exp = 1.0
        self.assertFloatEqual(obs, exp)

        max_d = 3.0
        d = 1.5
        obs = linear_weight(d,max_d)
        exp = 0.50
        self.assertFloatEqual(obs, exp)

    def test_assign_traits_to_tree(self):
        """assign_traits_to_tree should map reconstructed traits to tree nodes"""
        
        # Test that the function assigns traits from a dict to a tree node
        traits = self.SimpleTreeTraits
        tree = self.SimpleTree
        
        # Test on simple tree
        result_tree = assign_traits_to_tree(traits,tree)
        
        # Test that each node is assigned correctly
        for node in result_tree.preorder():
            obs = node.Reconstruction 
            exp = traits.get(node.Name, None)
            self.assertEqual(obs,exp)
        
        # Test on polytomy tree
        
        tree = self.SimplePolytomyTree
        result_tree = assign_traits_to_tree(traits,tree)
        
        # Test that each node is assigned correctly
        for node in result_tree.preorder():
            obs = node.Reconstruction 
            exp = traits.get(node.Name, None)
            self.assertEqual(obs,exp)

    def test_predict_traits_from_ancestors(self):
        """predict_traits_from_ancestors should propagate ancestral states"""
        traits = self.SimpleTreeTraits
        tree = self.SimpleTree
        
        #print "Starting tree:",tree.asciiArt()
        # Test on simple tree
        result_tree = assign_traits_to_tree(traits,tree)
        nodes_to_predict = [n.Name for n in result_tree.tips()]
        #print "Predicting nodes:", nodes_to_predict
        predictions = predict_traits_from_ancestors(result_tree,\
          nodes_to_predict)
       
        #print "Starting traits:", traits
        #print "Predictions:",predictions
        #for key in predictions.keys():
        #    
        #    print key,":",around(predictions[key])

        #TODO: Add the actual assertion here

    def test_fill_unknown_traits(self):
        """fill_unknown_traits should propagate only known characters"""


        # Only the missing values in to_update should be 
        # filled in with appropriate values from new
        to_update = array([1,0,1,None,1,0])
        new = array([None,None,1,1,1,1])
    
        obs = fill_unknown_traits(to_update,new)
        exp = array([1,0,1,1,1,0])

        self.assertTrue(array_equal(obs,exp))

        #Try the reverse update

        obs = fill_unknown_traits(new,to_update)
        exp = array([1,0,1,1,1,1])
        self.assertTrue(array_equal(obs,exp))

        # Ensure that if to_update is None, the value of new is returned
        obs = fill_unknown_traits(obs, exp)

    def test_weighted_average_tip_prediction(self):
        """Weighted average node prediction should predict node values"""
        
        
        # When the node is very close to I3, prediction should be approx. I3

        traits = self.PartialReconstructionTraits
        tree = assign_traits_to_tree(traits,self.CloseToI3Tree)
        node_to_predict = "A"
        prediction = weighted_average_tip_prediction(tree=tree,\
          node_to_predict=node_to_predict) 
        exp = traits["I3"]
        self.assertFloatEqual(around(prediction),exp)


        # When the node is very close to I1, prediction should be approx. I1


        traits = self.PartialReconstructionTraits
        tree = assign_traits_to_tree(traits,self.CloseToI1Tree)
        node_to_predict = "A"
        prediction = weighted_average_tip_prediction(tree=tree,\
          node_to_predict=node_to_predict) 
        exp = traits["I1"]
        self.assertFloatEqual(around(prediction),exp)

        # Try out the B case with exponential weighting
        
        traits = self.PartialReconstructionTraits
        tree = assign_traits_to_tree(traits,self.CloseToI3Tree)
        weight_fn = make_neg_exponential_weight_fn(exp_base=e)
        
        
        node_to_predict = "A"
        prediction = weighted_average_tip_prediction(tree=tree,\
          node_to_predict=node_to_predict,weight_fn=weight_fn) 
        exp = traits["B"]
        self.assertFloatEqual(around(prediction),exp)

        # Try out the I1 case with exponential weighting
        
        traits = self.PartialReconstructionTraits
        tree = assign_traits_to_tree(traits,self.CloseToI1Tree)
        weight_fn = make_neg_exponential_weight_fn(exp_base=e)
        #weight_fn = linear_weight
        
        node_to_predict = "A"
        prediction = weighted_average_tip_prediction(tree=tree,\
          node_to_predict=node_to_predict,weight_fn=weight_fn) 
        
        exp = traits["I1"]
        self.assertFloatEqual(around(prediction),exp)

        # Try out the balanced case where children and ancestors 
        # should be weighted a equally with exponential weighting
        
        # We'll  try this with full gene count data to ensure 
        # that case is tested

        traits = self.GeneCountTraits
        tree = assign_traits_to_tree(traits,self.BetweenI3AndI1Tree)
        weight_fn = make_neg_exponential_weight_fn(exp_base=e)
        
        node_to_predict = "A"
        prediction = weighted_average_tip_prediction(tree=tree,\
          node_to_predict=node_to_predict,weight_fn=weight_fn) 
        
        exp = (array(traits["I1"]) + array(traits["I3"]))/2.0
        self.assertFloatEqual(prediction,exp)

        #TODO: test the case with partial missing data (Nones)

        #TODO: test the case with fully missing data for either
        # the ancestor or the children. 

        #TODO: Test with polytomy trees

        # These *should* work, but until they're tested we don't know


if __name__ == "__main__":
    main()