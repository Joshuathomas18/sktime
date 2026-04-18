"""Tests for correct default metrics in deep learning regressors."""
import inspect
import pytest

def test_fcn_regressor_default_metric():
    from sktime.regression.deep_learning.fcn import FCNRegressor
    r = FCNRegressor()
    
    assert r.metrics is None
    
    src = inspect.getsource(r.build_model)
    assert "mean_squared_error" in src
    assert src.count('"accuracy"') == 0

def test_mlp_regressor_default_metric():
    from sktime.regression.deep_learning.mlp import MLPRegressor
    r = MLPRegressor()
    
    assert r.metrics is None
    
    src = inspect.getsource(r.build_model)
    assert "mean_squared_error" in src
    assert src.count('"accuracy"') == 0
