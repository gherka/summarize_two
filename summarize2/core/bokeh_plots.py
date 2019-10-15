import numpy as np
from numpy import linspace
from scipy.stats.kde import gaussian_kde
import pandas as pd
import json

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BasicTicker
from bokeh.layouts import column
from bokeh.models.callbacks import CustomJS
from bokeh.embed import json_item

from ..core.helper_funcs import transform_frequencies

def generate_diff_plot(df1, df2, var_name, shade):
	'''
	Plot the difference in frequency for each unique value of a given column (var_name).
	
	Returns a json representation of a Bokeh plot to be embedded in the template.
	'''

	if shade == 0:
		band_color = '#e6e5e3'
	else:
		band_color = 'gainsboro'

	freq_1, freq_2 = transform_frequencies(df1, df2, var_name)

	#make sure to sanitise names with an ' as JSON.parse will freak out.
	bokeh_df = pd.DataFrame({'VAR':[str(x).replace("'","") for x in freq_1[0]],
						'DF1':freq_1[1],
						'DF2':freq_2[1],
						'DIFF_ABS': freq_2[1] - freq_1[1],
						'DIFF_PCT': (freq_2[1] - freq_1[1]) / ((freq_2[1] + freq_1[1]) / 2),
						'COLOR': np.where(freq_2[1] - freq_1[1] > 0, '#527563', '#876388')}
					)

	source = ColumnDataSource(bokeh_df.sort_values(by='DIFF_PCT'))

	TOOLTIPS = [
		("Name", "@VAR"),
		("DF1 Value", "@DF1"),
		("DF2 Value", "@DF2"),
		("Absolute difference", "@DIFF_ABS"),
		("Percent difference", "@DIFF_PCT"),

	]

	p = figure(x_range=source.data['VAR'],
		plot_height=170,
		plot_width=165,
		tools="pan,wheel_zoom,hover",
		active_scroll="wheel_zoom",
		toolbar_location = None,
		tooltips=TOOLTIPS)

	p.vbar(x='VAR', top='DIFF_PCT', width=0.9, alpha=0.8, line_color='white', color='COLOR', source=source)
	p.ray(x=[0], y=[0], length=len(source.data['VAR']), angle=0, line_width=0.5, color='black')

	p.xaxis.visible = False
	p.yaxis.minor_tick_line_alpha = 0
	p.grid.visible = False
	p.background_fill_color = band_color
	p.outline_line_color = band_color
	p.border_fill_color = band_color
	p.yaxis.axis_line_width = 0.5

	item_text = json.dumps(json_item(p))

	return item_text

def generate_ridge_plot(df1, df2, spec):
	'''
	Given a ridge spec, generate a series of Bokeh plots showing
	histogram overlaid with KDE lines.
	'''

	DF1_COLOR = '#DD8452'
	DF2_COLOR = '#4C72B0'

	cols = spec['cols']
	num_col = spec['num_col']
	indices = spec['indices']

	temp_cats = [x[1] for x in indices if x[1] != '_']
	temp_df1 = df1.set_index(cols)[num_col]
	temp_df2 = df2.set_index(cols)[num_col]

	def make_plot(s1, s2, index, shade):

		#banded row colors: 
		if shade == 0:
			band_color = '#e6e5e3'
		else:
			band_color = 'gainsboro'


		bins = sorted(s1.append(s2).unique())

		hist1, edges1 = np.histogram(s1, density=False, bins=bins)
		hist2, edges2 = np.histogram(s2, density=False, bins=bins)

		plot_min = min(s1.values.min(), s2.values.min())
		plot_max = max(s1.values.max(), s2.values.max())

		x = linspace(plot_min, plot_max, 500)

		pdf1 = gaussian_kde(s1, bw_method=0.1)
		pdf2 = gaussian_kde(s2, bw_method=0.1)

		scale_factor = max(hist1.max(), hist2.max()) / max(pdf1(x).max(), pdf2(x).max())

		y1 = pdf1(x) * scale_factor
		y2 = pdf2(x) * scale_factor

		p = figure(plot_width=965, x_range=(plot_min, plot_max),
            active_scroll="wheel_zoom",
            tools="pan,wheel_zoom,reset")

		p.yaxis.axis_label = index
		p.yaxis.axis_label_standoff = 30

		p.line(x=x, y=y1, color=DF1_COLOR, alpha=1, line_width=1, muted_color=DF1_COLOR, muted_alpha=0.2, legend='PDF1')
		p.line(x=x, y=y2, color=DF2_COLOR, alpha=1, line_width=1, muted_color=DF2_COLOR, muted_alpha=0.2, legend='PDF2')

		hist1 = p.vbar(x=edges1[:-1], width=2, top=hist1, bottom=0,
      				   fill_color=DF1_COLOR, line_color=DF1_COLOR, alpha=0.75, line_alpha=0.4,
      				   muted_color=DF1_COLOR, muted_alpha=0.1, legend='HIST1')

		hist2 = p.vbar(x=edges2[:-1], width=2, top=hist2, bottom=0,
     				   fill_color=DF2_COLOR, line_color=DF2_COLOR, alpha=0.75, line_alpha=0.4,
      				   muted_color=DF2_COLOR, muted_alpha=0.1, legend='HIST2')

		hist1.muted = True
		hist2.muted = True

		#LEGEND
		p.legend.location = "top_right"
		p.legend.click_policy="mute"

		p.legend.background_fill_color = band_color
		p.legend.inactive_fill_color = band_color
		p.legend.border_line_color = band_color

		#STYLING
		p.outline_line_color = band_color
		p.background_fill_color = band_color

		p.border_fill_color = band_color

		p.ygrid.grid_line_color = None
		p.xgrid.grid_line_color = None
		p.xgrid.ticker = p.xaxis[0].ticker

		p.axis.minor_tick_line_color = None
		p.axis.major_tick_line_color = None
		p.axis.axis_line_color = None

		p.yaxis.major_label_text_color = "black"
		p.yaxis.major_label_text_font_size = "12px"
		p.xaxis.major_label_text_font_size = "11px"
		p.xaxis.major_label_text_font_style = "bold"

		return p

	plots = []

	for i, cat in enumerate(temp_cats):
		
		if len(cols) == 1:

			temp_s1 = temp_df1.xs(cat, level=None).dropna()
			temp_s2 = temp_df2.xs(cat, level=None).dropna()

			plots.append(make_plot(temp_s1, temp_s2, cat, i%2))

		else:

			temp_s1 = temp_df1.xs(cat, level=cols).dropna()
			temp_s2 = temp_df2.xs(cat, level=cols).dropna()

			plots.append(make_plot(temp_s1, temp_s2, ' | '.join(cat), i%2))


	p = column(plots)

	ridge_json = json.dumps(json_item(p))

	return ridge_json

def generate_kde_plot(df1, df2, col_name, shade):
	'''
	Using scipy's KDE implementation, create a KDE plot
	with a zoom and pan interactivity.
	'''

	s1 = df1[col_name].dropna()
	s2 = df2[col_name].dropna()

	#banded row colors:
	if shade == 0:
		band_color = "#e6e5e3"
	else:
		band_color = "gainsboro"

	DF1_COLOR = "#DD8452"
	DF2_COLOR = "#4C72B0"

	plot_min = min(s1.values.min(), s2.values.min())
	plot_max = max(s1.values.max(), s2.values.max())

	x = linspace(plot_min, plot_max, 500)

	pdf1 = gaussian_kde(s1, bw_method=0.1)
	pdf2 = gaussian_kde(s2, bw_method=0.1)

	y1 = pdf1(x)
	y2 = pdf2(x)

	#append zeroes to x and y to correctly position the patches as start and end points have to connect
	x = np.concatenate((np.concatenate(([plot_min], x)), [plot_max]))
	y1 = np.concatenate((np.concatenate(([0], y1)), [0]))
	y2 = np.concatenate((np.concatenate(([0], y2)), [0]))

	p = figure(plot_height=170, plot_width=165, x_range=(plot_min, plot_max),
		active_scroll="wheel_zoom",
		tools="pan,wheel_zoom,reset",
		toolbar_location=None)

	p.patch(x=x, y=y1, color=DF1_COLOR, alpha=0.25, line_alpha=1, line_width=1)
	p.patch(x=x, y=y2, color=DF2_COLOR, alpha=0.25, line_alpha=1, line_width=1)

	#STYLING
	p.outline_line_color = band_color
	p.background_fill_color = band_color
	p.border_fill_color = band_color

	p.ygrid.grid_line_color = None
	p.xgrid.grid_line_color = None

	p.yaxis.visible = False
	p.xaxis.ticker = BasicTicker(desired_num_ticks=2)

	p.yaxis.minor_tick_line_color = None
	p.axis.major_tick_line_color = None
	p.axis.axis_line_color = None

	kde_plot = json.dumps(json_item(p))
	return kde_plot