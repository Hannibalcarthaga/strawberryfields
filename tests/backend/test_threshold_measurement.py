# Copyright 2019 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""Unit tests for measurements in the Fock basis"""
import pytest
import numpy as np
from thewalrus.random import random_covariance
from thewalrus._torontonian import (
    tor,
    threshold_detection_prob_displacement,
    threshold_detection_prob,
    numba_tor,
    numba_ix,
    Qmat_numba,
    nb_block,
    powerset,
)
NUM_REPEATS = 50

@pytest.mark.backends("gaussian")
class TestGaussianRepresentation:
    """Tests that make use of the Fock basis representation."""

    def measure_threshold(self, setup_backend):
        """Tests that threshold_detection backend is implemented"""
        backend = setup_backend(3)
        backend.measure_threshold([0, 1], shots=5)
        
        n_modes = 5
        mu = np.zeros([2 * n_modes])
        cov = random_covariance(n_modes)
        prob = threshold_detection_prob_displacement(mu, cov, np.array([1] * n_modes))
        assert np.all(prob)

@pytest.mark.backends("gaussian")
class TestRepresentationIndependent:
    """Basic implementation-independent tests."""

    def test_two_mode_squeezed_measurements(self, setup_backend, pure):
        """Tests Threshold measurement on the two mode squeezed vacuum state."""
        for _ in range(NUM_REPEATS):
            backend = setup_backend(2)
            backend.reset(pure=pure)

            r = 0.25
            # Circuit to prepare two mode squeezed vacuum
            backend.squeeze(r, np.pi, 0)
            backend.squeeze(r, 0, 1)
            backend.beamsplitter(np.pi/4, np.pi, 0, 1)
            meas_modes = [0, 1]
            meas_results = backend.measure_threshold(meas_modes)
            assert np.all(meas_results[0][0] == meas_results[0][1])

    def test_vacuum_measurements(self, setup_backend, pure):
        """Tests Threshold measurement on the vacuum state."""
        backend = setup_backend(3)

        for _ in range(NUM_REPEATS):
            backend.reset(pure=pure)

            meas = backend.measure_threshold([0, 1, 2])[0]
            assert np.all(np.array(meas) == 0)


    def test_binary_outcome(self, setup_backend, pure):
        """Test that the outcomes of a threshold measurement is zero or one."""
        num_modes = 2
        for _ in range(NUM_REPEATS):
            backend = setup_backend(num_modes)
            backend.reset(pure=pure)

            r = 0.5
            backend.squeeze(r, 0, 0)
            backend.beamsplitter(np.pi/4, np.pi, 0, 1)
            meas_modes = [0, 1]
            meas_results = backend.measure_threshold(meas_modes)
            for i in range(num_modes):
                assert meas_results[0][i] == 0 or meas_results[0][i] == 1

