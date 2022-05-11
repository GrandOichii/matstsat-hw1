from sympy import *
from scipy.stats import t, f

class AnalisysResult:
    def __init__(self):
        self.latex_text: str = ''
        self.regression_pvalue: int = None
        self.regressor_pvalues: dict = {}

    def write_latex_to(self, path: str):
        with open('result.tex', 'w') as f:
            f.write(self.latex_text)

def analise(items: list, ykey='y', exclude_keys=None) -> AnalisysResult:
    result = AnalisysResult()

    if exclude_keys is None:
        exclude_keys = []

    result.latex_text = '\documentclass{article}\n\\usepackage{amsmath}\n\\begin{document}\n'

    n = len(items)
    result.latex_text += 'Number of observations ($n$) = ' + str(n) + '\n'

    regressorNames = []
    for key in items[0].keys():
        if key != 'mainPrice' and not key in exclude_keys:
            regressorNames += [key]

    k = len(regressorNames)

    result.latex_text += f'\n$k={k}$\n'

    result.latex_text += '\nRegression equation: \n'

    result.latex_text += '$Y_i=\\alpha+{}$\n'.format('+'.join([f'\\beta_{i+1}{regressorNames[i]}_i' for i in range(len(regressorNames))]))

    # calculate the y matrix
    yarr = []
    for item in items:
        yarr += [item[ykey]]

    ymat = Matrix(yarr)

    if shape(ymat)[0] > 4:
        result.latex_text += f'\n\n$Y=\\left[\\begin{{matrix}}{ymat[0]}\\\\{ymat[1]}\\\\{ymat[2]}\\\\\\cdots\\\\{ymat[-1]}\\end{{matrix}}\\right]$\n'
    else:
        result.latex_text += f'\n\n$Y={latex(ymat)}$\n'

    # calculate the x matrix
    xarr = []
    for item in items:
        arr = [1]
        for key in regressorNames:
            arr += [item[key]]
        xarr += [arr]
    xmat = Matrix(xarr)
    pprint(xmat)

    if shape(xmat)[0] > 4 and shape(xmat)[1] > 4:
        result.latex_text += f'\n\n$X=\\begin{{bmatrix}}{xmat[0, 0]} & {xmat[0, 1]} & {xmat[0, 2]} & \\dots  & {xmat[0, -1]} \\\\ {xmat[1, 0]} & {xmat[1, 1]} & {xmat[1, 2]} & \\dots  & {xmat[1, -1]} \\\\ \\vdots & \\vdots & \\vdots & \\ddots & \\vdots \\\\ {xmat[-1, 0]} & {xmat[-1, 1]} & {xmat[-1, 2]} & \\dots  & {xmat[-1, -1]}\\end{{bmatrix}}$\n'
    else:
        result.latex_text += f'\n\n$X={latex(xmat)}$\n'
    # calculate the estimates
    estimates = (xmat.T * xmat) ** -1 * xmat.T * ymat

    result.latex_text += f'\nCalculating the estimate $\\hat\\beta$ values\n'
    result.latex_text += f'\n$\\hat{{\\beta}}=(X^TX)^{{-1}}X^TY={latex(estimates)}$\n'

    result.latex_text += '\nRegression equation (with values): $Y_i={}{}$\n'.format(estimates[0], ''.join(['{}{}*{}'.format('+' if estimates[i+1] > 0 else '', estimates[i+1], regressorNames[i]) for i in range(len(regressorNames))]))

    # calculate the estimated y values
    estimatedY = xmat * estimates

    if shape(estimatedY)[0] > 4:
        result.latex_text += f'\n\nEstimated $Y$: $\\hat{{Y}}=\\left[\\begin{{matrix}}{estimatedY[0]}\\\\{estimatedY[1]}\\\\{estimatedY[2]}\\\\\\cdots\\\\{estimatedY[-1]}\\end{{matrix}}\\right]$\n'
    else:
        result.latex_text += f'\n\nEstimated $Y$: $Y={latex(estimatedY)}$\n'

    yaverage = sum(yarr)/len(yarr)

    result.latex_text += f'\n$\overline{{Y}}={yaverage}$\n'

    TSS = 0
    for y in yarr:
        TSS += (y - yaverage)**2
    tssf = '%.2f' % TSS
    result.latex_text += f'\n$TSS=\sum_{{t=1}}^{{n}} (Y_i-\overline{{Y}})^2={tssf}$\n'
    ESS = 0
    for y in estimatedY:
        ESS += (y - yaverage)**2
    essf = '%.2f' % ESS
    result.latex_text += f'\n$ESS=\sum_{{t=1}}^{{n}} (\hat{{Y_i}}-\overline{{Y}})^2={essf}$\n'
    RSS = TSS - ESS
    rssf = '%.2f' % RSS
    result.latex_text += f'\n$RSS=TSS-ESS={rssf}$\n'
    R2 = ESS/TSS
    r2f = '%.2f' % R2
    result.latex_text += f'\n$R^2=\\frac{{ESS}}{{TSS}}={r2f}$\n'

    sigma = RSS/(n - k - 1)
    sigmaf = '%.2f' % sigma
    result.latex_text += f'\n$\\hat{{\\sigma^2}}=\\frac{{RSS}}{{n-k-1}}={sigmaf}$\n'

    # calculate the v matrix
    vmat = sigma * ((xmat.T * xmat) ** -1)
    dispersions = []
    for i in range(1, k+1):
        d = vmat[i, i]
        dispersions += [d]

    result.latex_text += f'\n$\\hat{{V}}(\\hat{{\\beta}})=\\hat{{\\sigma^2}}(X^TX)^{{-1}}={latex(vmat)}\n'

    for i in range(len(regressorNames)):
        result.latex_text += f'\n$\\cdot$ Calculate the significance of value ${regressorNames[i]}_i$\n'

        result.latex_text += f'\n$H_o: \\hat{{\\beta_{i+1}}}=0$\n'
        result.latex_text += f'\n$H_a: \\hat{{\\beta_{i+1}}}\\neq0$\n'

        sq = sqrt(dispersions[i])
        result.latex_text += f'\n$\\hat{{D}}(\\hat{{\\beta_{i+1}}})=[\\hat{{V}}(\\hat{{\\beta}})]_{{{i+1} {i+1}}}={dispersions[i]}$\n'
        result.latex_text += f'\n$\\sqrt{{\\hat{{D}}(\\hat{{\\beta_{i+1}}})}}={latex(sq)}$\n'

        estimate = estimates[i+1]
        observed = estimate / sq
        result.latex_text += f'\n$\\hat{{\\beta_{i+1}}}={estimate}$\n'
        observedf = '%.2f' % float(observed)
        result.latex_text += f'\n$T_{{obs}}=\\frac{{\\hat{{\\beta_{i+1}}}-0}}{{\\sqrt{{\\hat{{D}}(\\hat{{\\beta_{i+1}}})}}}}={observedf}$\n'
        
        result.latex_text += '\n$T\\sim t(n-k-1)$\n'
        pvalue = 2 * t.cdf(float(-abs(observed)), n - k - 1)
        levelPC = pvalue * 100, 
        pvaluef = '%.4f' % pvalue
        levelPCf = '%.2f' % levelPC
        result.latex_text += f'\n$pvalue=P\\{{|T|>|T_{{obs}}|\\}}=2F(-|T_{{obs}}|)=2*tcdf(-|T_{{obs}}|, n-k-1)={pvaluef}\\approx{levelPCf}\\%$\n'

        result.regressor_pvalues[regressorNames[i]] = pvalue

    result.latex_text += '\n$\\cdot$ Check the validity of the entire regression equation\n'
    result.latex_text += '\n$H_o: '
    # for coef in regCoeffs:
    for i in range(len(regressorNames)):
        result.latex_text += f'\\beta_{i+1}='
    result.latex_text += '0$\n'
    result.latex_text += f'\n$H_a: |\\beta_1|'
    for i in range(1, len(regressorNames)):
        result.latex_text += '+|' + f'\\beta_{i+1}' + '|'
    result.latex_text += '\\neq0$\n'

    tobs = (R2 * (n-k-1)) / ((1 - R2) * k)
    tobsf = '%.2f' % tobs
    result.latex_text += f'\n$T_{{obs}}=\\frac{{R^2}}{{1-R^2}}*\\frac{{n-k-1}}{{k}}={tobsf}$\n'

    result.latex_text += f'\n$T\\sim F(k,n-k-1)$\n'

    pvalue = 1 - f.cdf(abs(float(tobs)), k, n-k-1)
    ppvalue = pvalue * 100
    pvaluef = '%.2f' % pvalue
    ppvaluef = '%.2f' % ppvalue
    result.regression_pvalue = pvalue
    result.latex_text += f'\n$pvalue=P(\\{{T>T_{{obs}}\\}})=1-F_T(T_{{obs}})=1-fcdf(|T_{{obs}}|,k,n-k-1)={pvaluef}\\approx{ppvaluef}\\%$\n'

    result.latex_text += '\\end{document}'
    return result