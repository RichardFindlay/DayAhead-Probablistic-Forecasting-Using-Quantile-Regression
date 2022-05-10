import pandas as pd
import numpy as np
import scipy
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from pickle import load


# declare model type
model_type = 'solar'

# load quantile prediction results
with open(f'../../results/{model_type}/forecasted_time_series_{model_type}.pkl', 'rb') as forecast_data:
	results = load(forecast_data)


# function to evaluate general & quantile performance
def evaluate_predictions(predictions):
	'''
	Theory from Bazionis & Georgilakis (2021): https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiUprb39qbyAhXNgVwKHWVsA50QFnoECAMQAQ&url=https%3A%2F%2Fwww.mdpi.com%2F2673-4826%2F2%2F1%2F2%2Fpdf&usg=AOvVaw1AWP-zHuNGrw8pgDfUS09e
	func to caluclate probablistic forecast performance
	Prediction Interval Coverage Probability (PICP)
	Prediction Interval Nominla Coverage (PINC)
	Average Coverage Error (ACE) [PICP - PINC]
	'''
	test_len = len(predictions['y_true'])

	print(test_len)

	y_true = predictions['y_true'].ravel()
	lower_pred = predictions[list(predictions.keys())[0]].ravel()
	upper_pred = predictions[list(predictions.keys())[-3]].ravel()
	central_case = predictions['0.5'].ravel()

	alpha = float(list(predictions.keys())[-3]) - float(list(predictions.keys())[0])

	# picp_ind = np.sum((y_true > lower_pred) & (y_true <= upper_pred))

	picp = ((np.sum((y_true > lower_pred) & (y_true <= upper_pred))) / (test_len * 48) ) * 100

	pinc = alpha * 100

	ace = (picp - pinc) # closer to '0' higher the reliability

	r = np.max(y_true) - np.min(y_true)

	# PI normalised width
	pinaw = (1 / (test_len * r)) * np.sum((upper_pred - lower_pred))

	# PI normalised root-mean-sqaure width 
	pinrw = (1/r) * np.sqrt( (1/test_len) * np.sum((upper_pred - lower_pred)**2))

	# calculate MAE & RMSE
	mae = mean_absolute_error(y_true, central_case)
	mape = mean_absolute_percentage_error(y_true, central_case)
	rmse = mean_squared_error(y_true, central_case, squared=False)

	# create pandas df
	metrics = pd.DataFrame({'PICP': picp, 'PINC': pinc, 'ACE': ace, 'PINAW': pinaw, 'PINRW': pinrw, 'MAE': mae, 'MAPE': mape, 'RMSE': rmse}, index={alpha})
	metrics.index.name = 'Prediction_Interval'

	print(metrics.to_string())

	# save performance metrics
	metrics.to_csv(f'../../results/{model_type}/preformance_summary_{model_type}.csv', index=False)

	return metrics


# function to evaluate trends
def correlation_analysis(X, Y):

	rs = np.empty((X.shape[0], 1))
	#caclulate 'R^2' for each feature - average over all days
	for l in range(X.shape[0]):
		slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(X[l,:,0], Y[l,:,0])
		rs[l, 0] =r_value**2
		
	print('mean' + '\n R**2: %s' %rs.mean())
	print('max' + '\n R**2: %s' %rs.max())
	print('min' + '\n R**2: %s' %rs.min())

	#get best
	best_fit = np.argmax(rs, axis=0)
	worst_fit = np.argmin(rs, axis=0)
	print(best_fit)
	print(worst_fit)

	return 



# call evaluate performance
evaluate_predictions(results)