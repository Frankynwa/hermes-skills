"""
Reusable numeric gradient checker that works without any external module (no eecs598 needed).
Works with Python 3.12+ and newer PyTorch (torch.nditer removed).

Usage:
    from numeric_gradient_check import numeric_gradient
    
    # Example: check gradient of a scalar-valued function
    err = gradient_check(my_loss_fn, W, analytic_dW, h=1e-6)
    assert err < 1e-5, f'Gradient check failed! Error: {err:.2e}'
"""
import torch
from itertools import product


def numeric_gradient(fn, x, h=1e-6):
    """Compute numeric gradient of scalar fn(x) w.r.t. x using central differences.
    
    Args:
        fn: function that takes a tensor and returns a scalar (tensor or float)
        x: input tensor (modified in-place during computation!)
        h: finite difference step size (default 1e-6)
    
    Returns:
        grad: numeric gradient tensor, same shape as x
    """
    grad = torch.zeros_like(x)
    for idx in product(*[range(s) for s in x.shape]):
        old_val = x[idx].item()
        x[idx] = old_val + h
        lp = fn(x)
        x[idx] = old_val - h
        lm = fn(x)
        x[idx] = old_val  # restore original value
        grad[idx] = (lp - lm) / (2 * h)
    return grad


def gradient_check(loss_fn, params, analytic_grad, h=1e-6):
    """Compute relative error between analytic and numeric gradient.
    
    Args:
        loss_fn: function that takes params and returns scalar loss
        params: input tensor (will be modified in-place)
        analytic_grad: the analytic gradient to compare against
        h: finite difference step size
    
    Returns:
        err: relative error (should be < 1e-5 for correct gradient)
    """
    numeric_grad = numeric_gradient(loss_fn, params.clone(), h=h)
    err = (analytic_grad - numeric_grad).abs().max() / (
        analytic_grad.abs().max() + numeric_grad.abs().max() + 1e-12
    )
    return err.item()
