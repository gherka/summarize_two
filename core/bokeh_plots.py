import numpy as np
from numpy import linspace
from scipy.stats.kde import gaussian_kde
import pandas as pd
import json

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.models.callbacks import CustomJS
from bokeh.embed import json_item

from core.helper_funcs import transform_frequencies

def generate_diff_plot(df1, df2, var_name, shade):
    '''
	Plot the difference in frequency for each unique value of a given column (var_name).
    
	Returns a json representation of a Bokeh plot to be embedded in the template.
    '''

    #banded row colors: 
    if shade == 'even':
        band_color = '#e6e5e3'
    else:
        band_color = 'gainsboro'

    freq_1, freq_2 = transform_frequencies(df1, df2, var_name)

	#make sure to sanitise names with an ' as JSON.parse will freak out.
    bokeh_df = pd.DataFrame({'VAR':[str(x).replace("'","") for x in freq_1[0]],
                        'DF1':freq_1[1],
                        'DF2':freq_2[1],
                        'DIFF': freq_2[1] - freq_1[1],
                        'COLOR': np.where(freq_2[1] - freq_1[1] > 0, '#527563', '#876388')}
                      )

    source = ColumnDataSource(bokeh_df.sort_values(by='DIFF'))

    TOOLTIPS = [
        ("Name", "@VAR"),
        ("DF1 Value", "@DF1"),
        ("DF2 Value", "@DF2"),
        ("Difference", "@DIFF")
    ]

    p = figure(x_range=source.data['VAR'],
           plot_height=170,
           plot_width=165,
           tools="pan,wheel_zoom,hover",
           active_scroll="wheel_zoom",
           toolbar_location = None,
           tooltips=TOOLTIPS)

    p.vbar(x='VAR', top='DIFF', width=0.9, alpha=0.8, line_color='white', color='COLOR', source=source)
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

def generate_ridge_plot(df1, df2, cols, num_col, indices):
	'''
	Need to investigate why plot is incorrect for arrays dominated by zeroes!
	'''

	DF1_COLOR = '#DD8452'
	DF2_COLOR = '#4C72B0'

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