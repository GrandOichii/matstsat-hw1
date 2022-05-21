from sympy import *
from scipy.stats import t, f

class AnalisysResult:
    def __init__(self):
        self.latex_text: str = ''
        self.regression_pvalue: int = None
        self.regressor_pvalues: dict = {}

    def write_latex_to(self, path: str):
        with open(path, 'w') as f:
            f.write(self.latex_text)

def analise(items: list, ykey='y', exclude_keys=None) -> AnalisysResult:
    result = AnalisysResult()

    if exclude_keys is None:
        exclude_keys = []

    result.latex_text = '\documentclass{article}\n\\usepackage{amsmath}\n\\begin{document}\n'

    n = len(items)
    result.latex_text += 'Number of observations ($n$) = ' + str(n) + '\n'

    regressorNames = []
    for key in items[0]['vars'].keys():
        if key != ykey and not key in exclude_keys:
            regressorNames += [key]

    k = len(regressorNames)

    result.latex_text += f'\n$k={k}$\n'

    result.latex_text += '\nRegression equation: \n'

    result.latex_text += '$Y_i=\\alpha+{}$\n'.format('+'.join([f'\\beta_{i+1}{regressorNames[i]}_i' for i in range(len(regressorNames))]))

    # calculate the y matrix
    yarr = []
    for item in items:
        yarr += [item['vars'][ykey]]

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
            arr += [item['vars'][key]]
        xarr += [arr]
    xmat = Matrix(xarr)

    if shape(xmat)[0] > 4 and shape(xmat)[1] > 4:
        result.latex_text += f'\n\n$X=\\begin{{bmatrix}}{xmat[0, 0]} & {xmat[0, 1]} & {xmat[0, 2]} & \\dots  & {xmat[0, -1]} \\\\ {xmat[1, 0]} & {xmat[1, 1]} & {xmat[1, 2]} & \\dots  & {xmat[1, -1]} \\\\ \\vdots & \\vdots & \\vdots & \\ddots & \\vdots \\\\ {xmat[-1, 0]} & {xmat[-1, 1]} & {xmat[-1, 2]} & \\dots  & {xmat[-1, -1]}\\end{{bmatrix}}$\n'
    else:
        result.latex_text += f'\n\n$X={latex(xmat)}$\n'
    # calculate the estimates
    estimates = (xmat.T * xmat) ** -1 * xmat.T * ymat
    
    result.latex_text += f'\nCalculating the estimate $\\hat\\beta$ values\n'
    result.latex_text += f'\n$\\hat{{\\beta}}=(X^TX)^{{-1}}X^TY={latex(estimates)}$\n'

    result.latex_text += '\nRegression equation (with values): $\\hat{{Y_i}}={}{}$\n'.format(estimates[0], ''.join(['{}{}*{}'.format('+' if estimates[i+1] > 0 else '', estimates[i+1], regressorNames[i]) for i in range(len(regressorNames))]))

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
    result.latex_text += f'\n$pvalue=P\\{{T>T_{{obs}}\\}}=1-F_T(T_{{obs}})=1-fcdf(|T_{{obs}}|,k,n-k-1)={pvaluef}\\approx{ppvaluef}\\%$\n'

    # do the chow tests
    for chow_key in items[0]['chowVars'].keys():
        result.latex_text += f'\\\\\\\\Chow tests:\n'
        result.latex_text += chow_test(items, ykey, chow_key, regressorNames, k)

    result.latex_text += '\\end{document}'
    return result

def chow_test(items: list, ykey: str, chow_key: str, regressorNames: list[str], k: int) -> str:
    result = ''
    result += f'\n$\cdot$ Testing {chow_key}\n'
    pile1 = []
    pile2 = []
    for item in items:
        if item['chowVars'][chow_key]:
            pile1 += [item]
        else:
            pile2 += [item]
    result += f'\nPile 1 ({chow_key} is true) size: {len(pile1)}\n'
    result += f'\nPile 2 ({chow_key} is false) size: {len(pile2)}\n'
    di = 'd^A_i'
    Amodel_latex = f'\\alpha^A{di}'
    for name in regressorNames:
        Amodel_latex += f'+\\beta^A_i{name}_i{di}'
    Amodel_latex = '\n$(A)Y_i=' + Amodel_latex + '+\\epsilon_i$\n'
    Bmodel_latex =  Amodel_latex.replace('A', 'B')
    result += Amodel_latex
    result += Bmodel_latex

    RSSall = calc_rss(items, ykey, regressorNames)
    RSSa = calc_rss(pile1, ykey, regressorNames)
    RSSb = calc_rss(pile2, ykey, regressorNames)

    # RSSall = 677043.679
    # RSSa = 9309.959
    # RSSb = 13940.942
    # k = 1

    result += '\n$RSS_{{all}}={}$\n'.format('%.2f' % RSSall)
    result += '\n$RSS_A={}$\n'.format('%.2f' % RSSa)
    result += '\n$RSS_B={}$\n'.format('%.2f' % RSSb)

    n = len(items)
    # n = 35
    tobs = ((RSSall - RSSa - RSSb) / (k + 1)) / ((RSSa+RSSb) / (n-2*k-2))

    result += '\n$T_{obs}=\\frac{(RSS_{all}-RSS_A-RSS_B)/(k+1)}{(RSS_A+RSS_B)/(n - 2k - 2)}=' + f'{tobs}$\n'
    tcrit = f.ppf(0.95, k + 1, n - 2 * k - 2)
    result += '\n$T_{crit}=finv(1 - SL, k + 1, n - 2k - 2)=' + f'{tcrit}$\n'
    if tobs > tcrit:
        result += '\n$T_{obs}>T_{crit}=>H_0$ is not valid $=>$ items should be split on ' + chow_key
    else:
        result += '\n$T_{obs}<T_{crit}=>H_0$ is valid $=>$ items should not be split on ' + chow_key
    return result

def calc_rss(items: list, ykey: str, regressorNames: list) -> int:
    yarr = []
    for item in items:
        yarr += [item['vars'][ykey]]
    ymat = Matrix(yarr)
    xarr = []
    for item in items:
        arr = [1]
        for key in regressorNames:
            arr += [item['vars'][key]]
        xarr += [arr]
    xmat = Matrix(xarr)    
    estimates = (xmat.T * xmat) ** -1 * xmat.T * ymat
    estimatedY = xmat * estimates
    yaverage = sum(yarr)/len(yarr)
    TSS = 0
    for y in yarr:
        TSS += (y - yaverage)**2
    ESS = 0
    for y in estimatedY:
        ESS += (y - yaverage)**2
    RSS = TSS - ESS
    return RSS