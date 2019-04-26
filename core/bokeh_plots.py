import numpy as np
from numpy import linspace
from scipy.stats.kde import gaussian_kde
import pandas as pd
import json

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.embed import json_item

from core.helper_funcs import transform_frequencies

def generate_diff_plot(df1, df2, var_name, shade):
    """
    Create a json representation of a Bokeh plot to be embedded in the template
    """

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

	def ridge(category, data, scale=5):
		return list(zip([category]*len(data), scale*data))

	#PREP THE DATA
	temp_cats = [x[1] for x in indices]

	temp_df1 = df1.set_index(cols)[num_col]
	temp_df2 = df2.set_index(cols)[num_col]

	bokeh_df1 = pd.concat([pd.DataFrame(data={' | '.join(x):temp_df1.xs(x, level=cols).values}) for x in temp_cats], axis=1)
	bokeh_df2 = pd.concat([pd.DataFrame(data={' | '.join(x):temp_df2.xs(x, level=cols).values}) for x in temp_cats], axis=1)

	#CREATE Y-AXIS
	cats = [' | '.join(x[1]).replace("'","") for x in indices]

	#CALCULATE X-AXIS LIMITS
	x_low = min(bokeh_df1.dropna().values.min(), bokeh_df2.dropna().values.min())
	x_high = max(bokeh_df1.dropna().values.max(), bokeh_df2.dropna().values.max())
	pc10 = (x_high - x_low) * 0.1

	#generate evenly spaced x values between min and max of the data
	x = linspace(x_low - pc10, x_high + pc10, 500)

	source1 = ColumnDataSource(data=dict(x=x))
	source2 = ColumnDataSource(data=dict(x=x))

	p = figure(y_range=cats, plot_width=965, x_range=(x_low - pc10, x_high + pc10),
				active_scroll="wheel_zoom",
				tools="pan,wheel_zoom,reset")

	p.toolbar.autohide = True

	glyph_list = []

	for i, cat in enumerate(cats):

		#what is the probability of a value to be in the x range?
		pdf1 = gaussian_kde(bokeh_df1[cat].dropna())
		pdf2 = gaussian_kde(bokeh_df2[cat].dropna())

		#Ridge function just scales the PDF(y)
		y1 = ridge(cat, pdf1(x))
		y2 = ridge(cat, pdf2(x))

		source1.add(y1, cat)
		source2.add(y2, cat)

		glyph_list.append((i, p.patch('x', cat, color='#DD8452', alpha=0.25, line_alpha=0.8, line_color='#DD8452', line_width=1, source=source2)))
		glyph_list.append((i, p.patch('x', cat, color='#4C72B0', alpha=0.25, line_alpha=0.8, line_color='#4C72B0', line_width=1, source=source1)))

	#STYLING
	p.outline_line_color = "gainsboro"
	p.background_fill_color = "gainsboro"

	p.border_fill_color = "gainsboro"

	p.ygrid.grid_line_color = None
	p.xgrid.grid_line_color = "#dddddd"
	p.xgrid.ticker = p.xaxis[0].ticker

	p.axis.minor_tick_line_color = None
	p.axis.major_tick_line_color = None
	p.axis.axis_line_color = None

	p.yaxis.major_label_text_color = "black"
	p.yaxis.major_label_text_font_size = "12px"
	p.xaxis.major_label_text_font_size = "11px"
	p.xaxis.major_label_text_font_style = "bold"

	#JS CALLBACK
	callback_glyphs = {'glyphs':glyph_list}

	code = """

	var y = Math.floor(cb_obj.y);

	for (let [index, glyph] of glyphs) 
		if (+index === +y) { 
		
			if ( glyph.visible ) { glyph.visible = false ;}
			else { glyph.visible = true }
		
		} ;

	"""
	#Have to strip control characters like new lines and tabs to keep JSON.parse() happy
	minified_code = code.replace("\n","").replace("\t","")
	
	callback = CustomJS(args=callback_glyphs, code=minified_code)

	p.js_on_event('tap', callback)

	ridge_json = json.dumps(json_item(p))

	return ridge_json