# -*- coding: utf-8 -*-

import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen


def adf_test(series, alpha=0.05):

    pass_test = False

    try:
        adf_result = adfuller(series)
        alpha = ''.join([str(int(alpha*100)), '%'])
        if adf_result[0] < adf_result[4][alpha]:
            pass_test = True
    except:
        return pass_test


def cadf_test(series1, series2, alpha=0.05):

    try:
        ols_model_1 = sm.OLS(series1, series2)
        ols_model_2 = sm.OLS(series2, series1)

        ols_result_1 = ols_model_1.fit()
        ols_result_2 = ols_model_2.fit()

        if ols_result_1.pvalues < ols_result_2.pvalues:
            series = ols_result_1.resid
            params = [1, ols_result_1.params]
        else:
            series = ols_result_2.resid
            params = [ols_result_2.params, 1]
        
        pass_test = adf_test(series, alpha)

        return pass_test, params
    
    except:
        return


def hurst_test(series, lags=20, benchmark=0.3):
    """Returns the Hurst Exponent of the time series vector series"""

    pass_test = False

    # Create the range of lag values
    lag_vector = range(2, lags)

    # Calculate the array of the variances of the lagged differences
    tau = [
        np.sqrt(
            np.std(np.subtract(series[lag:], series[:-lag]))
        ) for lag in lag_vector
    ]

    # Use a linear fit to estimate the Hurst Exponent
    poly = np.polyfit(np.log(lag_vector), np.log(tau), 1)
    hurst = poly[0] * 2

    if hurst <= benchmark:
        pass_test = True

    # Return the Hurst exponent from the np.polyfit output
    return pass_test


def johansen_test(matrix, det_order=0, lags=1, alpha=0.05):

    result = coint_johansen(matrix, det_order, lags)
    n_symbols = matrix.shape[1]
    trace_test = {}
    eig_test = {}

    try:
        crit = [0.1, 0.05, 0.01].index(alpha)

        for i in range(n_symbols):
            trace_test[i] = abs(result.lr1[i]) >= abs(result.cvt[i, crit])
            eig_test[i] = abs(result.lr2[i]) >= abs(result.cvm[i, crit])
        
        trace_rej_null = all(val is True for val in trace_test.values())
        eig_rej_null = all(val is True for val in eig_test.values())
        pass_test = trace_rej_null & eig_rej_null
    
    except Exception as e:
        raise ValueError(e)
    
    return pass_test, result.evec


def engle_granger_test(series1, series2, alpha=0.05):

    result = coint(series1, series2)
    pass_test = result[1] >= alpha

    return pass_test


def half_life_calc(matrix, eigenvector):
    
    yport = portfolio_val(matrix, eigenvector)
    
    deltaY = np.diff(yport)
    
    yy = np.vstack([yport[1:], np.ones(len(yport[1:]))]).T
    
    beta = np.linalg.lstsq(yy, deltaY)
    
    half_life = np.log(2)/beta[0]

    return half_life[0]


def portfolio_val(matrix, eigenvector):

    temp = np.matlib.repmat(eigenvector, len(matrix), 1)
    portfolio_val = np.sum(np.multiply(temp, matrix), 1)

    return portfolio_val