#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue May 31 16:55:10 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests on the machine infrastructure.
"""

import os, sys
import nose.tools
import math
import numpy

from . import Machine, PCATrainer
#from . import FisherLDATrainer, WhiteningTrainer, EMPCATrainer, WCCNTrainer


from xbob.learn.activation import HyperbolicTangent, Identity
from xbob.io import HDF5File

def F(f):
  """Returns the test file on the "data" subdirectory"""
  return __import__('pkg_resources').resource_filename(__name__, os.path.join('data', f))

MACHINE = F('linear-test.hdf5')

def test_initialization():

  # Two inputs and 1 output
  m = Machine(2,1)
  assert (m.weights == 0.0).all()
  nose.tools.eq_( m.weights.shape, (2,1) )
  assert (m.biases == 0.0).all()
  nose.tools.eq_( m.biases.shape, (1,) )

  # Start by providing the data
  w = numpy.array([[0.4, 0.1], [0.4, 0.2], [0.2, 0.7]], 'float64')
  m = Machine(w)
  b = numpy.array([0.3, -3.0], 'float64')
  isub = numpy.array([0., 0.5, 0.5], 'float64')
  idiv = numpy.array([0.5, 1.0, 1.0], 'float64')
  m.input_subtract = isub
  m.input_divide = idiv
  m.biases = b
  m.activation = HyperbolicTangent()

  assert (m.input_subtract == isub).all()
  assert (m.input_divide == idiv).all()
  assert (m.weights == w).all()
  assert (m.biases == b). all()
  nose.tools.eq_(m.activation, HyperbolicTangent())
  # Save to file
  # c = HDF5File("bla.hdf5", 'w')
  # m.save(c)

  # Start by reading data from a file
  c = HDF5File(MACHINE)
  m = Machine(c)
  assert (m.weights == w).all()
  assert (m.biases == b). all()

  # Makes sure we cannot stuff incompatible data
  w = numpy.array([[0.4, 0.4, 0.2], [0.1, 0.2, 0.7]], 'float64')
  m = Machine(w)
  b = numpy.array([0.3, -3.0, 2.7, -18, 52], 'float64') #wrong
  nose.tools.assert_raises(RuntimeError, setattr, m, 'biases', b)
  nose.tools.assert_raises(RuntimeError, setattr, m, 'input_subtract', b)
  nose.tools.assert_raises(RuntimeError, setattr, m, 'input_divide', b)

def test_correctness():

  # Tests the correctness of a linear machine
  c = HDF5File(MACHINE)
  m = Machine(c)

  def presumed(ivalue):
    """Calculates, by hand, the presumed output given the input"""

    # These are the supposed preloaded values from the file "MACHINE"
    isub = numpy.array([0., 0.5, 0.5], 'float64')
    idiv = numpy.array([0.5, 1.0, 1.0], 'float64')
    w = numpy.array([[0.4, 0.4, 0.2], [0.1, 0.2, 0.7]], 'float64')
    b = numpy.array([0.3, -3.0], 'float64')
    act = math.tanh

    return numpy.array([ act((w[i,:]*((ivalue-isub)/idiv)).sum() + b[i]) for i in range(w.shape[0]) ], 'float64')

  testing = [
      [1,1,1],
      [0.5,0.2,200],
      [-27,35.77,0],
      [12,0,0],
      ]

  # 1D case
  maxerr = numpy.ndarray((2,), 'float64')
  maxerr.fill(1e-10)
  for k in testing:
    input = numpy.array(k, 'float64')
    assert (abs(presumed(input) - m(input)) < maxerr).all()

  # 2D case
  output = m(testing)
  for i, k in enumerate(testing):
    input = numpy.array(k, 'float64')
    assert (abs(presumed(input) - output[i,:]) < maxerr).all()

def test_user_allocation():

  # Tests the correctness of a linear machine
  c = HDF5File(MACHINE)
  m = Machine(c)

  def presumed(ivalue):
    """Calculates, by hand, the presumed output given the input"""

    # These are the supposed preloaded values from the file "MACHINE"
    isub = numpy.array([0., 0.5, 0.5], 'float64')
    idiv = numpy.array([0.5, 1.0, 1.0], 'float64')
    w = numpy.array([[0.4, 0.4, 0.2], [0.1, 0.2, 0.7]], 'float64')
    b = numpy.array([0.3, -3.0], 'float64')
    act = math.tanh

    return numpy.array([ act((w[i,:]*((ivalue-isub)/idiv)).sum() + b[i]) for i in range(w.shape[0]) ], 'float64')

  testing = [
      [1,1,1],
      [0.5,0.2,200],
      [-27,35.77,0],
      [12,0,0],
      ]

  # 1D case
  maxerr = numpy.ndarray((2,), 'float64')
  maxerr.fill(1e-10)
  output = numpy.ndarray((2,), 'float64')
  for k in testing:
    input = numpy.array(k, 'float64')
    m(input, output)
    assert (abs(presumed(input) - output) < maxerr).all()

  # 2D case
  output = numpy.ndarray((len(testing), 2), 'float64')
  m(testing, output)
  for i, k in enumerate(testing):
    input = numpy.array(k, 'float64')
    assert (abs(presumed(input) - output[i,:]) < maxerr).all()

def test_comparisons():

  # Start by creating the data
  w1 = numpy.array([[0.4, 0.1], [0.4, 0.2], [0.2, 0.7]], 'float64')
  w2 = numpy.array([[0.4, 1.1], [0.4, 0.2], [0.2, 0.7]], 'float64')
  b1 = numpy.array([0.3, -3.0], 'float64')
  b2 = numpy.array([0.3, 3.0], 'float64')
  isub1 = numpy.array([0., 0.5, 0.5], 'float64')
  isub2 = numpy.array([0.5, 0.5, 0.5], 'float64')
  idiv1 = numpy.array([0.5, 1.0, 1.0], 'float64')
  idiv2 = numpy.array([1.5, 1.0, 1.0], 'float64')

  # Creates Machine's
  m1 = Machine(w1)
  m1.input_subtract = isub1
  m1.input_divide = idiv1
  m1.biases = b1
  m1.activation = HyperbolicTangent()

  m1b = Machine(m1)
  m1c = Machine(w1)
  m1c.input_subtract = isub1
  m1c.input_divide = idiv1
  m1c.biases = b1
  m1c.activation = HyperbolicTangent()

  m2 = Machine(w2)
  m2.input_subtract = isub1
  m2.input_divide = idiv1
  m2.biases = b1
  m2.activation = HyperbolicTangent()

  m3 = Machine(w1)
  m3.input_subtract = isub2
  m3.input_divide = idiv1
  m3.biases = b1
  m3.activation = HyperbolicTangent()

  m4 = Machine(w1)
  m4.input_subtract = isub1
  m4.input_divide = idiv2
  m4.biases = b1
  m4.activation = HyperbolicTangent()

  m5 = Machine(w1)
  m5.input_subtract = isub1
  m5.input_divide = idiv1
  m5.biases = b2
  m5.activation = HyperbolicTangent()

  m6 = Machine(w1)
  m6.input_subtract = isub1
  m6.input_divide = idiv1
  m6.biases = b1
  m6.activation = Identity()

  # Compares them using the overloaded operators == and !=
  assert m1 == m1b
  assert not m1 != m1b
  assert m1.is_similar_to(m1b)
  assert m1 == m1c
  assert not m1 != m1c
  assert m1.is_similar_to(m1c)
  assert not m1 == m2
  assert m1 != m2
  assert not m1.is_similar_to(m2)
  assert not m1 == m3
  assert m1 != m3
  assert not m1.is_similar_to(m3)
  assert not m1 == m4
  assert m1 != m4
  assert not m1.is_similar_to(m4)
  assert not m1 == m5
  assert m1 != m5
  assert not m1.is_similar_to(m5)
  assert not m1 == m6
  assert m1 != m6
  assert not m1.is_similar_to(m6)

def test_pca_settings():

  T = PCATrainer()
  assert T.use_svd == True
  T.use_svd = False
  assert T.use_svd == False

  T = PCATrainer(False)
  assert T.use_svd == False
  T.use_svd = True
  assert T.use_svd == True

def test_pca_versus_matlab_princomp():

  # Tests our SVD/PCA extractor.
  data = numpy.array([
      [2.5, 2.4],
      [0.5, 0.7],
      [2.2, 2.9],
      [1.9, 2.2],
      [3.1, 3.0],
      [2.3, 2.7],
      [2., 1.6],
      [1., 1.1],
      [1.5, 1.6],
      [1.1, 0.9],
      ], dtype='float64')

  # Expected results (from Matlab's princomp) - a good ground truth?
  eig_val_correct = numpy.array([1.28402771, 0.0490834], 'float64')
  eig_vec_correct = numpy.array([[-0.6778734, -0.73517866], [-0.73517866, 0.6778734]], 'float64')

  T = PCATrainer()
  machine_svd, eig_vals_svd = T.train(data)

  assert numpy.allclose(abs(machine_svd.weights/eig_vec_correct), 1.0)
  assert numpy.allclose(eig_vals_svd, eig_val_correct)
  assert machine_svd.weights.shape == (2,2)

  T.safe_svd = True
  machine_safe_svd, eig_vals_safe_svd = T.train(data)

  assert numpy.allclose(abs(machine_safe_svd.weights/eig_vec_correct), 1.0)
  assert numpy.allclose(eig_vals_safe_svd, eig_val_correct)
  assert machine_safe_svd.weights.shape == (2,2)

  T.use_svd = False #make it use the covariance method
  machine_cov, eig_vals_cov = T.train(data)

  assert numpy.allclose(abs(machine_cov.weights/eig_vec_correct), 1.0)
  assert numpy.allclose(eig_vals_cov, eig_val_correct)
  assert machine_cov.weights.shape == (2,2)

def test_pca_versus_matlab_princomp_2():

  # Tests our SVD/PCA extractor.
  data = numpy.array([
    [1,2, 3,5,7],
    [2,4,19,0,2],
    [3,6, 5,3,3],
    [4,8,13,4,2],
    ], dtype='float64')

  # Expected results (from Matlab's princomp) - a good ground truth?
  eig_val_correct = numpy.array([61.9870996, 9.49613738, 1.85009634], 'float64')

  # Train method 1
  T = PCATrainer()
  machine_svd, eig_vals_svd = T.train(data)

  assert numpy.allclose(eig_vals_svd, eig_val_correct)
  assert machine_svd.weights.shape == (5,3)

  machine_safe_svd, eig_vals_safe_svd = T.train(data)

  assert numpy.allclose(eig_vals_safe_svd, eig_val_correct)
  assert machine_safe_svd.weights.shape == (5,3)

  T.use_svd = False #make it use the covariance method
  machine_cov, eig_vals_cov = T.train(data)

  assert numpy.allclose(eig_vals_cov, eig_val_correct)
  assert machine_cov.weights.shape == (5,3)

def test_pca_trainer_comparisons():

  # Constructors and comparison operators
  t1 = PCATrainer()
  t2 = PCATrainer()
  t3 = PCATrainer(t2)
  t4 = t3
  assert t1 == t2
  assert t1.is_similar_to(t2)
  assert t1 == t3
  assert t1.is_similar_to(t3)
  assert t1 == t4
  assert t1.is_similar_to(t4)

  t5 = PCATrainer(False)
  t6 = PCATrainer(False)
  assert t5 == t6
  assert t5.is_similar_to(t6)
  assert t5 != t1

  t7 = PCATrainer(t1)
  assert t1 == t7
  t7.safe_svd = True
  assert t1 != t7
  t7.safe_svd = False
  assert t1 == t7


def test_pca_svd_vs_cov_random_1():

  # Tests our SVD/PCA extractor.
  data = numpy.random.rand(1000,4)

  # Train method 1
  T = PCATrainer()
  machine_svd, eig_vals_svd = T.train(data)
  T.safe_svd = True
  machine_safe_svd, eig_vals_safe_svd = T.train(data)
  T.use_svd = False #make it use the covariance method
  machine_cov, eig_vals_cov = T.train(data)

  assert numpy.allclose(eig_vals_svd, eig_vals_cov)
  assert machine_svd.weights.shape == (4,4)
  assert numpy.allclose(machine_svd.input_subtract, machine_cov.input_subtract)
  assert numpy.allclose(machine_svd.input_divide, machine_cov.input_divide)
  assert numpy.allclose(abs(machine_svd.weights/machine_cov.weights), 1.0)

  assert numpy.allclose(eig_vals_svd, eig_vals_safe_svd)
  assert numpy.allclose(machine_svd.input_subtract, machine_safe_svd.input_subtract)
  assert numpy.allclose(machine_svd.input_divide, machine_safe_svd.input_divide)
  assert numpy.allclose(abs(machine_svd.weights/machine_safe_svd.weights), 1.0)


def test_pca_svd_vs_cov_random_2():

  # Tests our SVD/PCA extractor.
  data = numpy.random.rand(15,60)

  # Train method 1
  T = PCATrainer()
  machine_svd, eig_vals_svd = T.train(data)
  T.safe_svd = True
  machine_safe_svd, eig_vals_safe_svd = T.train(data)
  T.use_svd = False #make it use the covariance method
  machine_cov, eig_vals_cov = T.train(data)

  assert numpy.allclose(eig_vals_svd, eig_vals_cov)
  assert machine_svd.weights.shape == (60,14)
  assert numpy.allclose(machine_svd.input_subtract, machine_cov.input_subtract)
  assert numpy.allclose(machine_svd.input_divide, machine_cov.input_divide)
  assert numpy.allclose(abs(machine_svd.weights/machine_cov.weights), 1.0)

  assert numpy.allclose(eig_vals_svd, eig_vals_safe_svd)
  assert numpy.allclose(machine_svd.input_subtract, machine_safe_svd.input_subtract)
  assert numpy.allclose(machine_svd.input_divide, machine_safe_svd.input_divide)
  assert numpy.allclose(abs(machine_svd.weights/machine_safe_svd.weights), 1.0)

@nose.tools.nottest
def test_fisher_lda_settings():

  t = FisherLDATrainer()
  assert t.use_pinv == False
  assert t.strip_to_rank == True

  t.use_pinv = True
  assert t.use_pinv
  t.strip_to_rank = False
  assert t.strip_to_rank == False

  t = FisherLDATrainer(use_pinv=True)
  assert t.use_pinv
  assert t.strip_to_rank

  t = FisherLDATrainer(strip_to_rank=False)
  assert t.use_pinv == False
  assert t.strip_to_rank == False

@nose.tools.nottest
def test_fisher_lda():

  # Tests our Fisher/LDA trainer for linear machines for a simple 2-class
  # "fake" problem:
  data = [
      numpy.array([
        [2.5, 2.4],
        [2.2, 2.9],
        [1.9, 2.2],
        [3.1, 3.0],
        [2.3, 2.7],
        ], dtype='float64'),
      numpy.array([
        [0.5, 0.7],
        [2., 1.6],
        [1., 1.1],
        [1.5, 1.6],
        [1.1, 0.9],
        ], dtype='float64'),
      ]

  # Expected results
  exp_trans_data = [
      [1.0019, 3.1205, 0.9405, 2.4962, 2.2949],
      [-2.9042, -1.3179, -2.0172, -0.7720, -2.8428]
      ]
  exp_mean = numpy.array([1.8100, 1.9100])
  exp_val = numpy.array([5.394526])
  exp_mach = numpy.array([[-0.291529], [0.956562]])

  T = FisherLDATrainer()
  machine, eig_vals = T.train(data)

  # Makes sure results are good
  assert numpy.alltrue(abs(machine.input_subtract - exp_mean) < 1e-6)
  assert numpy.alltrue(abs(machine.weights - exp_mach) < 1e-6)
  assert numpy.alltrue(abs(eig_vals - exp_val) < 1e-6)

  # Use the pseudo-inverse method
  T.use_pinv = True
  machine_pinv, eig_vals_pinv = T.train(data)

  # Makes sure results are good
  assert numpy.alltrue(abs(machine_pinv.input_subtract - exp_mean) < 1e-6)
  assert numpy.alltrue(abs(eig_vals_pinv - exp_val) < 1e-6)

  # Eigen vectors could be off by a constant
  weight_ratio = machine_pinv.weights[0] / machine.weights[0]
  normalized_weights = (machine_pinv.weights.T/weight_ratio).T
  assert numpy.allclose(machine.weights, normalized_weights)

@nose.tools.nottest
def test_fisher_lda_bis():

  # Tests our Fisher/LDA trainer for linear machines for a simple 2-class
  # "fake" problem:
  data = [
      numpy.array([
        [2.5, 2.4, 2.5],
        [2.2, 2.9, 3.],
        [1.9, 2.2, 2.],
        [3.1, 3.0, 3.1],
        [2.3, 2.7, 2.4],
        ], dtype='float64'),
      numpy.array([
        [-0.5, -0.7, -1.],
        [-2., -1.6, -2.],
        [-1., -1.1, -1.],
        [-1.5, -1.6, -1.6],
        [-1.1, -0.9, -1.],
        ], dtype='float64'),
      ]

  # Expected results after resizing
  exp_mean = numpy.array([0.59, 0.73, 0.64])
  exp_val = numpy.array([33.9435556])
  exp_mach = numpy.array([[0.14322439], [-0.98379062], [0.10790173]])

  T = FisherLDATrainer()
  machine, eig_vals = T.train(data)

  # Makes sure results are good
  machine.resize(3,1) # eigenvalue close to 0 are not significant (just keep the first one)
  assert numpy.alltrue(abs(machine.input_subtract - exp_mean) < 1e-6)
  assert numpy.alltrue(abs(eig_vals[0:1] - exp_val[0:1]) < 1e-6)
  assert numpy.alltrue(abs(machine.weights[:,0] - exp_mach[:,0]) < 1e-6)

  # Use the pseudo-inverse method
  T.use_pinv = True
  machine_pinv, eig_vals_pinv = T.train(data)

  # Makes sure results are good
  machine_pinv.resize(3,1) # eigenvalue close to 0 are not significant (just keep the first one)
  assert numpy.alltrue(abs(machine_pinv.input_subtract - exp_mean) < 1e-6)
  assert numpy.alltrue(abs(eig_vals_pinv[0:1] - exp_val[0:1]) < 1e-6)

  # Eigen vectors could be off by a constant
  weight_ratio = machine_pinv.weights[0] / machine.weights[0]
  normalized_weights = (machine_pinv.weights.T/weight_ratio).T
  assert numpy.allclose(machine.weights, normalized_weights)

@nose.tools.nottest
def test_fisher_lda_comparisons():

  # Constructors and comparison operators
  t1 = FisherLDATrainer()
  t2 = FisherLDATrainer()
  t3 = FisherLDATrainer(t2)
  t4 = t3
  assert t1 == t2
  assert t1.is_similar_to(t2)
  assert t1 == t3
  assert t1.is_similar_to(t3)
  assert t1 == t4
  assert t1.is_similar_to(t4)

  t3 = FisherLDATrainer(use_pinv=True)
  t4 = FisherLDATrainer(use_pinv=True)
  assert t3 == t4
  assert t3.is_similar_to(t4)
  assert t3 != t1
  assert not t3.is_similar_to(t2)

@nose.tools.nottest
def test_ppca():

  # Tests our Probabilistic PCA trainer for linear machines for a simple
  # problem:
  ar=numpy.array([
    [1, 2, 3],
    [2, 4, 19],
    [3, 6, 5],
    [4, 8, 13],
    ], dtype='float64')

  # Expected llh 1 and 2 (Reference values)
  exp_llh1 =  -32.8443
  exp_llh2 =  -30.8559

  # Do two iterations of EM to check the training procedure
  T = EMPCATrainer()
  m = LinearMachine(3,2)
  # Initialization of the trainer
  T.initialize(m, ar)
  # Sets ('random') initialization values for test purposes
  w_init = numpy.array([1.62945, 0.270954, 1.81158, 1.67002, 0.253974,
    1.93774], 'float64').reshape(3,2)
  sigma2_init = 1.82675
  m.weights = w_init
  T.sigma2 = sigma2_init
  # Checks that the log likehood matches the reference one
  # This should be sufficient to check everything as it requires to use
  # the new value of W and sigma2
  # This does an E-Step, M-Step, computes the likelihood, and compares it to
  # the reference value obtained using matlab
  T.e_step(m, ar)
  T.m_step(m, ar)
  llh1 = T.compute_likelihood(m)
  assert abs(exp_llh1 - llh1) < 2e-4
  T.e_step(m, ar)
  T.m_step(m, ar)
  llh2 = T.compute_likelihood(m)
  assert abs(exp_llh2 - llh2) < 2e-4

@nose.tools.nottest
def test_whitening_initialization():

  # Constructors and comparison operators
  t1 = WhiteningTrainer()
  t2 = WhiteningTrainer()
  t3 = WhiteningTrainer(t2)
  t4 = t3
  assert t1 == t2
  assert t1.is_similar_to(t2)
  assert t1 == t3
  assert t1.is_similar_to(t3)
  assert t1 == t4
  assert t1.is_similar_to(t4)

@nose.tools.nottest
def test_whitening_train():

  # Tests our Whitening extractor.
  data = numpy.array([[ 1.2622, -1.6443, 0.1889],
                      [ 0.4286, -0.8922, 1.3020],
                      [-0.6613,  0.0430, 0.6377],
                      [-0.8718, -0.4788, 0.3988],
                      [-0.0098, -0.3121,-0.1807],
                      [ 0.4301,  0.4886, -0.1456]])
  sample = numpy.array([1, 2, 3.])

  # Expected results (from matlab)
  mean_ref = numpy.array([0.096324163333333, -0.465965438333333, 0.366839091666667])
  whit_ref = numpy.array([[1.608410253685985,                  0,                  0],
                          [1.079813355720326,  1.411083365535711,                  0],
                          [0.693459921529905,  0.571417184139332,  1.800117179839927]])
  sample_whitened_ref = numpy.array([5.942255453628436, 4.984316201643742, 4.739998188373740])

  # Runs whitening (first method)
  t = WhiteningTrainer()
  m = LinearMachine(3,3)
  t.train(m, data)
  s = m.forward(sample)

  # Makes sure results are good
  eps = 1e-4
  assert numpy.allclose(m.input_subtract, mean_ref, eps, eps)
  assert numpy.allclose(m.weights, whit_ref, eps, eps)
  assert numpy.allclose(s, sample_whitened_ref, eps, eps)

  # Runs whitening (second method)
  m2 = t.train(data)
  s2 = m2.forward(sample)

  # Makes sure results are good
  eps = 1e-4
  assert numpy.allclose(m2.input_subtract, mean_ref, eps, eps)
  assert numpy.allclose(m2.weights, whit_ref, eps, eps)
  assert numpy.allclose(s2, sample_whitened_ref, eps, eps)

@nose.tools.nottest
def test_wccn_initialization():

  # Constructors and comparison operators
  t1 = WCCNTrainer()
  t2 = WCCNTrainer()
  t3 = WCCNTrainer(t2)
  t4 = t3
  assert t1 == t2
  assert t1.is_similar_to(t2)
  assert t1 == t3
  assert t1.is_similar_to(t3)
  assert t1 == t4
  assert t1.is_similar_to(t4)

@nose.tools.nottest
def test_wccn_train():

  # Tests our Whitening extractor.
  data = [numpy.array([[ 1.2622, -1.6443, 0.1889], [ 0.4286, -0.8922, 1.3020]]),
          numpy.array([[-0.6613,  0.0430, 0.6377], [-0.8718, -0.4788, 0.3988]]),
          numpy.array([[-0.0098, -0.3121,-0.1807],  [ 0.4301,  0.4886, -0.1456]])]
  sample = numpy.array([1, 2, 3.])

  # Expected results
  mean_ref = numpy.array([ 0.,  0.,  0.])
  weight_ref = numpy.array([[ 15.8455444 ,  0.        ,  0.       ],
                            [-10.7946764 ,  2.87942129,  0.       ],
                            [ 18.76762201, -2.19719292,  2.1505817]])
  sample_wccn_ref = numpy.array([50.55905765, -0.83273618, 6.45174511])

  # Runs WCCN (first method)
  t = WCCNTrainer()
  m = LinearMachine(3,3)
  t.train(m, data)
  s = m.forward(sample)

  # Makes sure results are good
  eps = 1e-4
  assert numpy.allclose(m.input_subtract, mean_ref, eps, eps)
  assert numpy.allclose(m.weights, weight_ref, eps, eps)
  assert numpy.allclose(s, sample_wccn_ref, eps, eps)

  # Runs WCCN (second method)
  m2 = t.train(data)
  s2 = m2.forward(sample)

  # Makes sure results are good
  eps = 1e-4
  assert numpy.allclose(m2.input_subtract, mean_ref, eps, eps)
  assert numpy.allclose(m2.weights, weight_ref, eps, eps)
  assert numpy.allclose(s2, sample_wccn_ref, eps, eps)
