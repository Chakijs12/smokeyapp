histDotSizePNG = 0.5    # can have decimals, like 0.5

fadeoutime = 0.79247   ### for ui, only ingame

dataTimerUpdate = 0.02

sCustomFontName='Segoe UI'                  ### default
#sCustomFontName='Segoe UI; Weight=Light'
#sCustomFontName='Consolas'
#sCustomFontName='Arial'
### you can try some others if curious
#sCustomFontName="Ticking Timebomb BB"      # font might be installed from some other app
#sCustomFontName="Digital-7"                # font might be installed from some other app
#sCustomFontName="Strait"                   # font might be installed from some other app

userChanged=True  ### False - will auto-adjust to max g-forces ; True - auto off




import ac, acsys, sys, os, platform, traceback, math, json, time, threading
from configparser import ConfigParser

os.environ['PATH'] = os.environ['PATH'] + ";."
if platform.architecture()[0] == "64bit":
  sysdir='apps/python/GForce/DLLs/stdlib64'
else:
  sysdir='apps/python/GForce/DLLs/stdlib'
sys.path.insert(0, sysdir)
from gfsim_info import info

sys.path.insert(0, 'apps/python/system')
# https://pypi.org/project/Pillow/2.4.0/
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageEnhance

bCSPActive = False
if 'ext_createRenderTarget' in dir(ac) and 'ext_generateMips' in dir(ac):
  bCSPActive = True

canvasGF=0
myImageGF=0
rtIndexGF = -1
rtIndex0 = -1
PNGmultGF = 1.0
gSteeringNormalizer = 90

timerIMG = 0.0
timerIMG2 = 0.0
ac_angle          = { "FL" : 0.0, "FR" : 0.0, "RL" : 0.0, "RR" : 0.0 }
ac_SlipRatio      = { "FL" : 0.0, "FR" : 0.0, "RL" : 0.0, "RR" : 0.0 }
ac_wspeed         = { "FL" : 0.0, "FR" : 0.0, "RL" : 0.0, "RR" : 0.0 }
datagf=0
wmain=-1
hmain=wmain
thread = 0

appSettingsPath         = "apps\\python\\GForce\\settings\\settings.ini"
appSettingsDefaultsPath = "apps\\python\\GForce\\settings\\settings_defaults.ini"

# defaults
# dont change here, all read from "settings.ini" or "settings_defaults.ini"
saveResults    = False # SAVERESULTS
DoResetOnUSERFFBChange = False
g_Reset_When_In_Pits = True
jsonPower=0.0

showGForce     = True
showTyres      = True
showTraction   = True
showPedals     = True
showFFB        = True
showLabels     = True
showGBars      = True
showHeader     = False
zForce         = False
centeredZForce = False
showArcade     = True
bScaleFixed    = True
gforce_fac     = 2
texid          = 2
gColor         = 1
gSizeGforce    = 100
gSizeSub       = 100
histCount      = 0
histVisi       = 0
smoothValue    = 10
gOpacityBG     = 0
gOpacityBGSub  = 0
gOpacityFG     = 100
gOpacityTx     = 100
gOpacityHL     = 100
bGreen   = True
bYellow  = True
bOrange  = True
bRed     = True
bBlue    = True
ghistT   = 70 # history transparency
f1=0
txcnt=-1

gforce_x_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
gforce_y_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
gforce_z_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
###
VisiMult        = 1
dataTimer       = 0.0

revRange = []
Gears    = []
geardatacount = 0
geardatacountdone = 0

# combined from all four wheels
LimitGreen      = 0.25   # green      TyreSlip    # ac_WSlip
LimitYellow     = 100    # yellow     Mz          # ac_Mz
LimitOrange     = 0.01   # orange     SlipRatio   # ac_SR
LimitRed        = 1.0    # red        NDSlip      # ac_NdSlip
LimitBlue       = 8.0    # blue       SlipAngle   # ac_SA

# min diff btw traction circles
Divoffset       = 3
DivGreen        = 50+Divoffset*2
DivYellow       = 50+Divoffset
DivOrange       = 50
DivRed          = 50-Divoffset
DivBlue         = 50-Divoffset*2

b_Green   = 0
b_Yellow  = 0
b_Orange  = 0
b_Red     = 0
b_Blue    = 0
b_arcade  = 0
#
maxG_XGREpos=0.5 # 0.5
maxG_XYELpos=0.5 # 0.55
maxG_XORApos=0.5 # 0.60
maxG_XREDpos=0.5 # 0.65
maxG_XBLUpos=0.5 # 0.70
maxG_XGREneg=0.5 # 0.5
maxG_XYELneg=0.5 # 0.55
maxG_XORAneg=0.5 # 0.60
maxG_XREDneg=0.5 # 0.65
maxG_XBLUneg=0.5 # 0.70
maxG_YGREpos=0.5 # 0.5
maxG_YYELpos=0.5 # 0.55
maxG_YORApos=0.5 # 0.60
maxG_YREDpos=0.5 # 0.65
maxG_YBLUpos=0.5 # 0.70
maxG_YGREneg=0.5 # 0.5
maxG_YYELneg=0.5 # 0.55
maxG_YORAneg=0.5 # 0.60
maxG_YREDneg=0.5 # 0.65
maxG_YBLUneg=0.5 # 0.70
valx=0.0
valy=0.0
valxx=0.0
valyy=0.0

#####################################################################
base_gforce_fac          = 2.0
max_gforce_fac = base_gforce_fac

maxHistCount    = 500
lastCarFFB = 0.0

# dont set this, it will be calculated from gSizeGforce anyway, which is changeble
fontSize    = int(float(gSizeGforce/7.0))

lastXYZ   = [[111.0,111.0,111.0] * maxHistCount for i in range(maxHistCount)]
lastXY    = [[111.0,111.0]       * maxHistCount for i in range(maxHistCount)]

currID  = 0
carName = ""
currentCar = 0
isInPits = False
bDoneResetInPits = False

appWindow = 0
b_gforceDec = 0
b_gforceInc = 0
b_showGForce = 0
b_showTyres  = 0
b_showPedals = 0
b_showTraction = 0
b_showLabels = 0
b_saveResults = 0
b_saveResultsNow = 0
b_showGBars = 0
b_showFFB = 0
b_Temp = 0
b_Press = 0
b_reset = 0
b_doResetOnFFB = 0
b_vertToggle = 0
b_color = 0
b_texid = 0
b_smoothValueUp = 0
b_smoothValueDn = 0
b_TrailDn = 0
b_TrailUp = 0
b_TrailSmoothDn = 0
b_TrailSmoothUp = 0
b_SizeDec = 0
b_SizeInc = 0
b_transpBGUp = 0
b_transpBGDn = 0
b_transpTxUp = 0
b_transpTxDn = 0
b_transpFGUp = 0
b_transpFGDn = 0
b_transpHLUp = 0 # highlight
b_transpHLDn = 0 # highlight
b_transpGUp = 0
b_transpGDn = 0
b_transphistUp = 0
b_transphistDn = 0
b_histDotSizeDec = 0
b_histDotSizeInc = 0
b_DotSizeDec = 0
b_DotSizeInc = 0
DotSize         = 10
histDotSize     = 1.0
gOpacityG = 50
TempID=0
PressID=0

bActiveTimer = True
fTimer  = 5.0
fTimer2 = 0.0
texid0 = 0
texid1 = 0
texid2 = 0
texid3 = 0
texid4 = 0
texid5 = 0
box_w=0
box_w2=0
box_h=0
box_h2=0
offset=0
top=0
texture_dot       = 0
texture_dot2      = 0
texture_gforce    = 0
texture_gforce_1g = 0
texture_gforce_2g = 0
texture_gforce_3g = 0
texture_gforce_4g = 0
texture_circle    = 0
texidNW=0
texidNE=0
texidSW=0
texidSE=0
texidN=0
texidS=0

ac_SR             = [0.0,0.0,0.0,0.0]
ac_SA             = [0.0,0.0,0.0,0.0]
ac_NdSlip         = [0.0,0.0,0.0,0.0]
ac_press          = [0.0,0.0,0.0,0.0]
ac_temp           = [0.0,0.0,0.0,0.0]
ac_dirt           = [0.0,0.0,0.0,0.0]
ac_Mz             = [0.0,0.0,0.0,0.0]
ac_speed          = 0
ac_throttle       = 0
ac_brake          = 0

gforce_x =0
gforce_y=0
gforce_z=0
ac_ffb=0
ac_WSlip=[0.0,0.0,0.0,0.0]

##########################################################################
class FontMeasures:
  def __init__(self, name, italic, bold, size, ratio, distance, heightCompensation, widthCompensation):
    self.n = name					#font name
    self.i = italic					#font italic
    self.b = bold					#font bold
    self.s = size					#font multiplier for one pixel height
    self.r = ratio					#font width compared to height
    self.d = distance				#font distance between the leftmost point of one letter and another, avareage
    self.h = heightCompensation		#font height offset to put it centered vertically
    self.w = widthCompensation		#font width offset to put it centered horizontally
    self.f = 0						#font object to be used in rendering
    return

class ExtGL:
  CULL_MODE_FRONT = 0
  CULL_MODE_BACK = 1
  CULL_MODE_NONE = 2
  CULL_MODE_WIREFRAME = 4
  CULL_MODE_WIREFRAME_SMOOTH = 7
  BLEND_MODE_OPAQUE = 0
  BLEND_MODE_ALPHA_BLEND = 1
  BLEND_MODE_ALPHA_TEST = 2
  BLEND_MODE_ALPHA_ADD = 4
  BLEND_MODE_MULTIPLY_BOTH = 5
  FONT_ALIGN_LEFT = 0
  FONT_ALIGN_RIGHT = 1
  FONT_ALIGN_CENTER = 2

def onGforceDec(dummy, variable):
  global bCSPActive, rtIndexGF, rtIndex0, max_gforce_fac, base_gforce_fac, gforce_fac, userChanged
  userChanged=True
  if base_gforce_fac>1.1:
      base_gforce_fac-=0.5
  max_gforce_fac = base_gforce_fac
  gforce_fac = max_gforce_fac
  appCreatePilImages()
  if bCSPActive and rtIndexGF>-1:
    ac.ext_clearRenderTarget(rtIndexGF)
    ac.ext_clearRenderTarget(rtIndex0)
  appResize()

def onGforceInc(dummy, variable):
  global bCSPActive, rtIndexGF, rtIndex0, max_gforce_fac, base_gforce_fac, gforce_fac, userChanged
  userChanged=True
  if base_gforce_fac<5:
      base_gforce_fac+=0.5
  max_gforce_fac = base_gforce_fac
  gforce_fac = max_gforce_fac
  appCreatePilImages()
  if bCSPActive and rtIndexGF>-1:
    ac.ext_clearRenderTarget(rtIndexGF)
    ac.ext_clearRenderTarget(rtIndex0)
  appResize()


def apphistDotSizeUp(*args):
  global histDotSize
  histDotSize += 0.1
  if histDotSize>4.0:
    histDotSize = 4.0
  appResize()

def apphistDotSizeDn(*args):
  global histDotSize
  histDotSize -= 0.1
  if histDotSize<0.5:
    histDotSize = 0.5
  appResize()

def appDotSizeUp(*args):
  global DotSize
  DotSize += 1
  if DotSize>50:
    DotSize = 50
  appResize()

def appDotSizeDn(*args):
  global DotSize
  DotSize -= 1
  if DotSize<1:
    DotSize = 1
  appResize()



def ondoResetOnFFB(*args):
  global DoResetOnUSERFFBChange
  DoResetOnUSERFFBChange = not DoResetOnUSERFFBChange
  # appResize()
  on_click_app_window()

def getSetting(cfgdef, cfg, sect, value, valdef):
  res = valdef
  if cfgdef.has_option(sect, value):
    res = cfgdef[sect][value]
    if ';' in res:
      res = res.split(';')[0]
    if cfg.has_option(sect, value):
      res = cfg[sect][value]
      if ';' in res:
        res = res.split(';')[0]
  return str(res)

def str2bool(v):
  return str(v).lower() in ("yes", "true", "t", "1")

def get_numbers(s):
  result=""
  idx=0
  for l in s.strip():
    if l.isnumeric() or l=='.' or (idx<1 and l=='-'):
      result=result+l
    else:
      break
    idx+=1
  if result=="" or result=="-" or result==".":
    return ''
  return float(result)



def appCreatePilImages():
  global myImageGF, canvasGF
  myImageGF = Image.open('apps/python/GForce/gforce_blanc.png')
  canvasGF = ImageDraw.Draw(myImageGF)
  myImageGF.putalpha(0)

def onReset(*args):
  global l_gforce, gforce_max, gforce_fac, gforce_last, base_gforce_fac, currentCar
  global maxG_XGREpos, maxG_YGREpos, maxG_XYELpos, maxG_YYELpos, maxG_XORApos, maxG_YORApos, maxG_XREDpos, maxG_YREDpos
  global maxG_XYELneg, maxG_YYELneg, maxG_XORAneg, maxG_YORAneg, maxG_XREDneg, maxG_YREDneg, lastCarFFB
  global maxG_XGREneg, maxG_YGREneg, maxG_XBLUpos, maxG_YBLUpos, maxG_XBLUneg, maxG_YBLUneg
  global bCSPActive, rtIndexGF, rtIndex0, myImageGF

  appCreatePilImages()
  if bCSPActive and rtIndexGF>-1:
    ac.ext_clearRenderTarget(rtIndexGF)
    ac.ext_clearRenderTarget(rtIndex0)

  maxG_XGREpos=0.5 # 0.5
  maxG_XYELpos=0.5 # 0.55
  maxG_XORApos=0.5 # 0.60
  maxG_XREDpos=0.5 # 0.65
  maxG_XBLUpos=0.5 # 0.70
  maxG_XGREneg=0.5 # 0.5
  maxG_XYELneg=0.5 # 0.55
  maxG_XORAneg=0.5 # 0.60
  maxG_XREDneg=0.5 # 0.65
  maxG_XBLUneg=0.5 # 0.70
  maxG_YGREpos=0.5 # 0.5
  maxG_YYELpos=0.5 # 0.55
  maxG_YORApos=0.5 # 0.60
  maxG_YREDpos=0.5 # 0.65
  maxG_YBLUpos=0.5 # 0.70
  maxG_YGREneg=0.5 # 0.5
  maxG_YYELneg=0.5 # 0.55
  maxG_YORAneg=0.5 # 0.60
  maxG_YREDneg=0.5 # 0.65
  maxG_YBLUneg=0.5 # 0.70

  gforce_fac   = base_gforce_fac
  gforce_last  = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
  gforce_max   = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
  ac.setText(l_gforce[0], "")
  ac.setText(l_gforce[1], "")
  ac.setText(l_gforce[2], "")
  ac.setText(l_gforce[3], "")
  ac.setText(l_gforce[4], "")
  ac.setText(l_gforce[5], "")
  if showFFB:
    ac.setText(l_gforce[6], "ffb: {:.2f}\n0".format(gforce_max[6]))
  else:
    ac.setText(l_gforce[6], "")

  if len(args)>0 and bool(args[0]):
    appResize()













def acShutdown():
  global appSettingsPath, gColor, zForce, centeredZForce, gSizeGforce, gOpacityBG, gOpacityFG, gOpacityTx, base_gforce_fac, bScaleFixed
  global showGForce, showTyres, showPedals, showTraction, showLabels, texid, histCount, histVisi, smoothValue, TempID, PressID, showFFB, showGBars, DoResetOnUSERFFBChange
  global gOpacityHL, b_transpHLUp, b_transpHLDn, carName, gOpacityG, ghistT, saveResults
  global canvasGF, PNGmultGF, datagf, histDotSize, Gears
  try:
    t1=time.time()
    if saveResults:
      appSaveImages('')

    if bCSPActive and  rtIndex0>-1:
      ac.ext_disposeRenderTarget(rtIndexGF)
      ac.ext_disposeRenderTarget(rtIndex0)

    config = ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_"), comment_prefixes=(";","#","/","_"))
    config.optionxform = str
    config.read(appSettingsPath)
    if not config.has_section('GENERAL'):
      config.add_section('GENERAL')

    config['GENERAL']['SAVERESULTS']          = str(saveResults)
    config['GENERAL']['DOTSIZE']              = str(int(DotSize))
    config['GENERAL']['HISTDOTSIZE']          = str(round(histDotSize,1))
    config['GENERAL']['APPSIZE']              = str(gSizeGforce)
    config['GENERAL']['BGOPACITY']            = str(gOpacityBG)
    config['GENERAL']['TXOPACITY']            = str(gOpacityTx)
    config['GENERAL']['FGOPACITY']            = str(gOpacityFG)
    config['GENERAL']['HLOPACITY']            = str(gOpacityHL)
    config['GENERAL']['GOPACITY']             = str(gOpacityG)
    config['GENERAL']['HISTORYOPACITY']       = str(ghistT)
    config['GENERAL']['COLOR']                = str(gColor)
    config['GENERAL']['SHOWVERTICALG']        = str(zForce)
    config['GENERAL']['VERTICALGCENTERED']    = str(centeredZForce)
    config['GENERAL']['SHOWGFORCE']           = str(showGForce)
    config['GENERAL']['SHOWPEDALS']           = str(showPedals)
    config['GENERAL']['SHOWTRACTION']         = str(showTraction)
    config['GENERAL']['SHOWTYRES']            = str(showTyres )
    config['GENERAL']['SHOWLABELS']           = str(showLabels)
    config['GENERAL']['SHOWMAXONLY']          = str(showGBars)
    config['GENERAL']['SHOWFFB']              = str(showFFB)
    config['GENERAL']['TEXTUREID']            = str(int(texid))
    config['GENERAL']['TRAILLENGHT']          = str(int(histCount))
    config['GENERAL']['TRAILVISIBILITY']      = str(int(histVisi))
    config['GENERAL']['SMOOTHVALUE']          = str(round(smoothValue,1))
    config['GENERAL']['RESETONUSERFFBCHANGE'] = str(DoResetOnUSERFFBChange)
    if TempID==0:
      config['GENERAL']['TEMPID']  ='Celsius'
    else:
      config['GENERAL']['TEMPID']  ='Fahrenheit'
    if PressID==0:
      config['GENERAL']['PRESSID'] ='bar'
    else:
      config['GENERAL']['PRESSID'] ='psi'

    config['GENERAL']['TRACTGREEN']  = str(bGreen)
    config['GENERAL']['TRACTYELLOW'] = str(bYellow)
    config['GENERAL']['TRACTORANGE'] = str(bOrange)
    config['GENERAL']['TRACTRED']    = str(bRed)
    config['GENERAL']['TRACTBLUE']   = str(bBlue)
    config['GENERAL']['ARCADE']      = str(showArcade)

    #config['GENERAL']['SCALEFIXED']           = str(bScaleFixed)
    #config['GENERAL']['GFORCEFACT'] =str(float(base_gforce_fac ))
    if not config.has_section('CAR_GFACTOR'):
      config.add_section('CAR_GFACTOR')
    config['CAR_GFACTOR'][carName] = str( round(float(base_gforce_fac), 1) )

    with open(appSettingsPath, 'w') as configfile:
      config.write(configfile, space_around_delimiters=False)

    ac.log('g-force saving images: ' + str(round(time.time()-t1,3))+'sec')

    # for i in range(len(Gears)):
    #   ac.log('gear ' + str(i))
    #   ac.log(str(Gears[i]))

  except:
    ac.log('error: ' + traceback.format_exc() )







def acMain(ac_version):
  global l_gforce, l_tyre, TempID, PressID, act_idx, act_idx2, showGForce, showTyres, showPedals, showLabels, saveResults, showTraction
  global gforce_x_act, gforce_y_act, gforce_z_act, gforce_last, gforce_max, max_gforce_fac, histCount, maxHistCount, histVisi, smoothValue
  global box_w, box_w2, box_h, box_h2, top, appWindow, fontSize, b_vertToggle, b_reset, b_color, b_doResetOnFFB
  global gOpacityBG, gOpacityFG, gOpacityTx, gColor, zForce, centeredZForce, gSizeGforce, base_gforce_fac
  global appSettingsPath, appSettingsDefaultsPath, texture_dot2
  global b_showGForce, b_showTyres, b_showPedals, b_showTraction, b_showLabels, b_saveResults, b_saveResultsNow, b_texid, b_gforceDec, b_gforceInc, b_arcade
  global b_TrailSmoothDn, b_TrailSmoothUp, b_smoothValueUp, b_smoothValueDn, b_Temp, b_Press, b_TrailDn, b_TrailUp, b_transpFGDn, b_transpFGUp, b_transpTxDn, b_transpTxUp
  global texid, texid0, texid1, texid2, texid3, texid4, texid5, texture_circle, texture_gforce, texture_gforce_1g, texture_gforce_2g, texture_gforce_3g, texture_gforce_4g, b_showFFB, showFFB, showGBars, b_showGBars
  global texidNW, texidNE, texidSW, texidSE, texture_dot, DoResetOnUSERFFBChange, carName, userChanged
  global b_Green, b_Yellow, b_Orange, b_Red, b_Blue, texidN, texidS
  global bGreen, bYellow, bOrange, bRed, bBlue, showArcade
  global gOpacityHL, b_transpHLUp, b_transpHLDn, bScaleFixed, sCustomFontName
  global b_transpGUp, b_transpGDn, gOpacityG
  global b_transphistUp, b_transphistDn, ghistT, f1
  global b_SizeDec, b_SizeInc, b_transpBGDn, b_transpBGUp
  global gSizeSub, gOpacityBGSub, b_histDotSizeDec, b_histDotSizeInc, histDotSize
  global g_Reset_When_In_Pits, bCSPActive
  global b_DotSizeDec, b_DotSizeInc, DotSize

  try:

    ### app windows
    appWindow = ac.newApp("GForce")
    ac.drawBorder(appWindow, 0)
    ac.setBackgroundOpacity(appWindow, 0)

    if bCSPActive:
      f1 = FontMeasures(sCustomFontName, 0, 0, 1.25, 0.69, 0.629, 0.616, 0.066)
      f1.f = ac.ext_glFontCreate(f1.n, f1.s, f1.i, f1.b)

    texture_gforce_1g = ac.newTexture("apps/python/GForce/gforce_1g.png")
    texture_gforce_2g = ac.newTexture("apps/python/GForce/gforce_2g.png")
    texture_gforce_3g = ac.newTexture("apps/python/GForce/gforce_3g.png")
    texture_gforce_4g = ac.newTexture("apps/python/GForce/gforce_4g.png")
    texture_circle    = ac.newTexture("apps/python/GForce/circle.png")
    texid0            = ac.newTexture("apps/python/GForce/gforce_92px.png")
    texid1            = ac.newTexture("apps/python/GForce/gforce_92px2.png")
    texid2            = ac.newTexture("apps/python/GForce/gforce_92px3.png")
    texid3            = ac.newTexture("apps/python/GForce/gforce_92px4.png")
    texid4            = ac.newTexture("apps/python/GForce/gforce_92px5.png")
    texid5            = ac.newTexture("apps/python/GForce/gforce_92px6.png")
    texture_dot       = ac.newTexture("apps/python/GForce/gforce_dot4.png")
    texture_dot2      = ac.newTexture("apps/python/GForce/gforce_dot4_2.png")
    texidNW           = ac.newTexture("apps/python/GForce/circle_NW.png")
    texidNE           = ac.newTexture("apps/python/GForce/circle_NE.png")
    texidSW           = ac.newTexture("apps/python/GForce/circle_SW.png")
    texidSE           = ac.newTexture("apps/python/GForce/circle_SE.png")
    texidN            = ac.newTexture("apps/python/GForce/circle_N.png")
    texidS            = ac.newTexture("apps/python/GForce/circle_S.png")
    texture_gforce   = texid0
    if   texid==1:
      texture_gforce = texid1
    elif texid==2:
      texture_gforce = texid2
    elif texid==3:
      texture_gforce = texid3
    elif texid==4:
      texture_gforce = texid4
    elif texid>=5:
      texture_gforce = texid5

    configdefault = ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_",","), comment_prefixes=(";","#","/","_",","))
    configdefault.optionxform = str
    configdefault.read(appSettingsDefaultsPath)

    try:
      if os.path.isfile(appSettingsPath):
        config = ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_",","), comment_prefixes=(";","#","/","_",","))
        config.optionxform = str
        with open(appSettingsPath, 'r', 'utf8') as f:
          lines=[]
          lines = f.read().split('\n')
          l=len(lines)
          while l<len(lines)-1:
            if l!='' and l[0]=='=':
              lines

        config.read(appSettingsPath)
      else:
        config = configdefault
    except:
      lines=[]
      with open(appSettingsPath, 'r') as f:
        lines = f.read().split('\n')
      l=len(lines)-1
      while l>0:
        if lines[l]!='' and lines[l][0]=='=':
          lines.pop(l)
          l-=1
        l-=1
      config.read_string(('\n'.join(x for x in lines)))
      with open(appSettingsPath, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)

    # bScaleFixed              = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SCALEFIXED'          , str(bScaleFixed) ) )
    DotSize                  = int(float(      getSetting(configdefault, config, 'GENERAL', 'DOTSIZE'             , str(DotSize  ) ) ) )
    histDotSize              =     float(      getSetting(configdefault, config, 'GENERAL', 'HISTDOTSIZE'         , str(float(histDotSize) ) ) )
    gOpacityBG               = int(float(      getSetting(configdefault, config, 'GENERAL', 'BGOPACITY'           , str(gOpacityBG  ) ) ) )
    gOpacityTx               = int(float(      getSetting(configdefault, config, 'GENERAL', 'TXOPACITY'           , str(gOpacityTx  ) ) ) )
    gOpacityFG               = int(float(      getSetting(configdefault, config, 'GENERAL', 'FGOPACITY'           , str(gOpacityFG  ) ) ) )
    gOpacityHL               = int(float(      getSetting(configdefault, config, 'GENERAL', 'HLOPACITY'           , str(gOpacityHL  ) ) ) )
    gOpacityG                = int(float(      getSetting(configdefault, config, 'GENERAL', 'GOPACITY'            , str(gOpacityG  ) ) ) )
    ghistT                   = int(float(      getSetting(configdefault, config, 'GENERAL', 'HISTORYOPACITY'      , str(ghistT) ) ) )
    gSizeGforce              = int(float(      getSetting(configdefault, config, 'GENERAL', 'APPSIZE'             , str(gSizeGforce) ) ) )
    gSizeSub                 = int(float(      getSetting(configdefault, config, 'GENERAL', 'SUBAPPSIZE'          , str(gSizeSub) ) ) )
    gColor                   = int(float(      getSetting(configdefault, config, 'GENERAL', 'COLOR'               , str(gColor) ) ) )
    zForce                   = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWVERTICALG'       , str(zForce) ) )
    centeredZForce           = str2bool(       getSetting(configdefault, config, 'GENERAL', 'VERTICALGCENTERED'   , str(centeredZForce) ) )
    showGForce               = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWGFORCE'          , str(showGForce) ) )
    showTyres                = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWTYRES'           , str(showTyres) ) )
    showPedals               = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWPEDALS'          , str(showPedals) ) )
    showTraction             = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWTRACTION'        , str(showTraction) ) )
    showLabels               = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWLABELS'          , str(showLabels) ) )
    saveResults              = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SAVERESULTS'         , str(saveResults) ) )
    showGBars                = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWMAXONLY'         , str(showGBars) ) )
    showFFB                  = str2bool(       getSetting(configdefault, config, 'GENERAL', 'SHOWFFB'             , str(showFFB) ) )
    texid                    = int(            getSetting(configdefault, config, 'GENERAL', 'TEXTUREID'           , str(texid) ) )
    histCount                = int(            getSetting(configdefault, config, 'GENERAL', 'TRAILLENGHT'         , str(histCount) ) )
    histVisi                 = int(            getSetting(configdefault, config, 'GENERAL', 'TRAILVISIBILITY'     , str(histVisi) ) )
    smoothValue              = int(            getSetting(configdefault, config, 'GENERAL', 'SMOOTHVALUE'         , str(smoothValue) ) )
    DoResetOnUSERFFBChange   = str2bool(       getSetting(configdefault, config, 'GENERAL', 'RESETONUSERFFBCHANGE', str(DoResetOnUSERFFBChange) ) )
    g_Reset_When_In_Pits     = str2bool(       getSetting(configdefault, config, 'GENERAL', 'RESETWHENINPITS'     , str(g_Reset_When_In_Pits) ) )
    base_gforce_fac          =     float(      getSetting(configdefault, config, 'GENERAL', 'GFORCEFACT'          , str(base_gforce_fac) ) )
    max_gforce_fac = base_gforce_fac

    bGreen     = str2bool(       getSetting(configdefault, config, 'GENERAL', 'TRACTGREEN' , str(bGreen) ) )
    bYellow    = str2bool(       getSetting(configdefault, config, 'GENERAL', 'TRACTYELLOW', str(bYellow) ) )
    bOrange    = str2bool(       getSetting(configdefault, config, 'GENERAL', 'TRACTORANGE', str(bOrange) ) )
    bRed       = str2bool(       getSetting(configdefault, config, 'GENERAL', 'TRACTRED'   , str(bRed) ) )
    bBlue      = str2bool(       getSetting(configdefault, config, 'GENERAL', 'TRACTBLUE'  , str(bBlue) ) )
    showArcade = str2bool(       getSetting(configdefault, config, 'GENERAL', 'ARCADE'     , str(showArcade) ) )

    carName = ac.getCarName(0)
    CAR_JSON_PATH = "content/cars/%s/ui/ui_car.json" % carName
    try:
      with open(CAR_JSON_PATH, "r", encoding="utf-8") as FP:
        CAR_JSON = json.load(FP, strict=False)
        CAR_POWER = get_numbers(CAR_JSON["specs"]["bhp"])
        if CAR_POWER != '':
          jsonPower = CAR_POWER
    except:
      ac.log("G-Force: JSON read error: %s" % CAR_JSON_PATH)
    if config.has_section('CAR_GFACTOR') and config.has_option('CAR_GFACTOR', carName):
      base_gforce_fac = max(1.0, float( config['CAR_GFACTOR'][carName] ) )
      max_gforce_fac = float(base_gforce_fac)
      userChanged = True
    # else:
    #   try:
    #     with open(CAR_JSON_PATH, "r", encoding="utf-8") as FP:
    #       CAR_JSON = json.load(FP, strict=False)
    #       CAR_MASS = get_numbers(CAR_JSON["specs"]["weight"])
    #       CAR_POWER =get_numbers(CAR_JSON["specs"]["bhp"])
    #       base_gforce_fac =  min(base_gforce_fac, max(1.0, float( math.floor( (CAR_MASS-75) / CAR_POWER / 2 ) ) ) )  ### +0.5
    #       max_gforce_fac = base_gforce_fac
    #   except:
    #     ac.log("G-Force: JSON read error: %s" % CAR_JSON_PATH)

    TempID = 1
    if getSetting(configdefault, config, 'GENERAL', 'TEMPID', 'Celsius') == 'Celsius':
      TempID = 0
    PressID = 0
    if getSetting(configdefault, config, 'GENERAL', 'PRESSID', 'bar') != 'bar':
      PressID = 1

    l_gforce     = [0,0,0,0,0,0,0]
    gforce_last  = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    gforce_max   = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    l_tyre       = [0,0,0,0]
    act_idx = 0
    act_idx2 = 0

    # g forces labels
    l_gforce[0] = ac.addLabel(appWindow, "")
    l_gforce[1] = ac.addLabel(appWindow, "")
    l_gforce[2] = ac.addLabel(appWindow, "")
    l_gforce[3] = ac.addLabel(appWindow, "")
    l_gforce[4] = ac.addLabel(appWindow, "")
    l_gforce[5] = ac.addLabel(appWindow, "")
    l_gforce[6] = ac.addLabel(appWindow, "")
    # tyre infos
    l_tyre[0] = ac.addLabel(appWindow, "")
    l_tyre[1] = ac.addLabel(appWindow, "")
    l_tyre[2] = ac.addLabel(appWindow, "")
    l_tyre[3] = ac.addLabel(appWindow, "")

    ac.setCustomFont(l_gforce[0], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[1], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[2], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[3], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[4], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[5], sCustomFontName, 0, 0)
    ac.setCustomFont(l_gforce[6], sCustomFontName, 0, 0)
    ac.setCustomFont(l_tyre[0]  , sCustomFontName, 0, 0)
    ac.setCustomFont(l_tyre[1]  , sCustomFontName, 0, 0)
    ac.setCustomFont(l_tyre[2]  , sCustomFontName, 0, 0)
    ac.setCustomFont(l_tyre[3]  , sCustomFontName, 0, 0)

    b_gforceInc = ac.addButton(appWindow, "+")
    b_gforceDec = ac.addButton(appWindow, "-")

    b_reset = ac.addButton(appWindow, "reset")
    b_doResetOnFFB = ac.addButton(appWindow, "reset on\nNum+/-")
    b_vertToggle = ac.addButton(appWindow, "z0")
    b_color = ac.addButton(appWindow, "c0")
    b_texid  = ac.addButton(appWindow, "t0")

    b_smoothValueUp = ac.addButton(appWindow, "+")
    b_smoothValueDn = ac.addButton(appWindow, "-")
    b_TrailUp = ac.addButton(appWindow, '   + trails')
    b_TrailDn = ac.addButton(appWindow, "-" )
    b_TrailSmoothUp = ac.addButton(appWindow, "+")
    b_TrailSmoothDn = ac.addButton(appWindow, "-" )
    b_transpBGUp = ac.addButton(appWindow, "+")
    b_transpBGDn = ac.addButton(appWindow, "- bg")
    b_transpTxUp = ac.addButton(appWindow, "+")
    b_transpTxDn = ac.addButton(appWindow, "- tx")
    b_transpFGUp = ac.addButton(appWindow, "+")
    b_transpFGDn = ac.addButton(appWindow, "- fg")
    b_transpHLUp = ac.addButton(appWindow, "+")
    b_transpHLDn = ac.addButton(appWindow, "- hl")

    b_transpGUp = ac.addButton(appWindow, "+")
    b_transpGDn = ac.addButton(appWindow, "- bgG")

    b_transphistUp = ac.addButton(appWindow, "+")
    b_transphistDn = ac.addButton(appWindow, "- history")

    b_arcade  = ac.addButton(appWindow, "arcade")

    b_Green   = ac.addButton(appWindow, "")
    b_Yellow  = ac.addButton(appWindow, "")
    b_Orange  = ac.addButton(appWindow, "")
    b_Red     = ac.addButton(appWindow, "")
    b_Blue    = ac.addButton(appWindow, "")

    b_showGForce    = ac.addButton(appWindow, "x")
    b_showTyres     = ac.addButton(appWindow, "x")
    b_showPedals    = ac.addButton(appWindow, "x")
    b_showTraction  = ac.addButton(appWindow, "x")
    b_showFFB       = ac.addButton(appWindow, "x")
    b_showLabels    = ac.addButton(appWindow, "x")
    b_showGBars     = ac.addButton(appWindow, "x")
    b_Temp          = ac.addButton(appWindow, "C")
    b_Press         = ac.addButton(appWindow, "p")

    b_saveResults   = ac.addButton(appWindow, "x")
    b_saveResultsNow= ac.addButton(appWindow, "save png's now")
    b_SizeInc       = ac.addButton(appWindow, "+")
    b_SizeDec       = ac.addButton(appWindow, "-" )

    b_histDotSizeDec    = ac.addButton(appWindow, "+")
    b_histDotSizeInc    = ac.addButton(appWindow, "-" )
    b_DotSizeDec        = ac.addButton(appWindow, "+")
    b_DotSizeInc        = ac.addButton(appWindow, "-" )

    ac.setFontColor(b_Green   , 0.5 , 1   , 0.5  , 1)
    ac.setFontColor(b_Yellow  , 1   , 1   , 0.5  , 1)
    ac.setFontColor(b_Orange  , 1   , 0.6 , 0.3 , 1)
    ac.setFontColor(b_Red     , 1   , 0.6 , 0.6  , 1)
    ac.setFontColor(b_Blue    , 0.6 , 0.6 , 1    , 1)

    ac.setFontAlignment(b_TrailDn, "left")
    ac.setFontAlignment(b_smoothValueDn, "left")
    ac.setFontAlignment(b_TrailSmoothDn, "left")
    ac.setFontAlignment(b_transpBGDn, "left")
    ac.setFontAlignment(b_transpTxDn, "left")
    ac.setFontAlignment(b_transpFGDn, "left")
    ac.setFontAlignment(b_transpHLDn, "left")

    ac.setFontAlignment(b_TrailUp, "left")
    ac.setFontAlignment(b_smoothValueUp, "right")
    ac.setFontAlignment(b_TrailSmoothUp, "right")
    ac.setFontAlignment(b_transpBGUp, "right")
    ac.setFontAlignment(b_transpTxUp, "right")
    ac.setFontAlignment(b_transpGUp, "right")
    ac.setFontAlignment(b_transphistDn, "center")
    ac.setFontAlignment(b_transpFGUp, "right")
    ac.setFontAlignment(b_transpHLUp, "right")
    ac.setSize(b_histDotSizeDec     , 35, 40)
    ac.setSize(b_histDotSizeInc     , 35, 40)
    ac.setSize(b_DotSizeDec     , 35, 40)
    ac.setSize(b_DotSizeInc     , 35, 40)

    ac.setSize(b_reset          , 80, 40)
    ac.setSize(b_doResetOnFFB   , 80, 40)
    ac.setSize(b_vertToggle     , 35, 40)
    ac.setSize(b_color          , 35, 40)
    ac.setSize(b_texid          , 35, 40)
    ac.setSize(b_gforceDec      , 25, 40)
    ac.setSize(b_gforceInc      , 25, 40)
    ac.setSize(b_smoothValueDn  , 25, 40)
    ac.setSize(b_smoothValueUp  , 25, 40)
    ac.setSize(b_TrailDn        , 25, 40)
    ac.setSize(b_TrailUp        , 25, 40)
    ac.setSize(b_TrailSmoothDn  , 25, 40)
    ac.setSize(b_TrailSmoothUp  , 25, 40)
    ac.setSize(b_SizeDec        , 25, 40)
    ac.setSize(b_SizeInc        , 25, 40)
    ac.setSize(b_transpBGDn     , 35, 40)
    ac.setSize(b_transpBGUp     , 35, 40)

    ac.setSize(b_transpTxDn     , 35, 40)
    ac.setSize(b_transpTxUp     , 35, 40)
    ac.setSize(b_transpGDn      , 35, 40)
    ac.setSize(b_transpGUp      , 35, 40)
    ac.setSize(b_transphistUp   , 50, 40)
    ac.setSize(b_transphistDn   , 50, 40)

    ac.setSize(b_showTyres      , 65, 24)
    ac.setSize(b_showPedals     , 65, 24)
    ac.setSize(b_showGForce     , 65, 24)
    ac.setSize(b_showTraction   , 65, 24)
    ac.setSize(b_showFFB        , 65, 24)
    ac.setSize(b_showLabels     , 65, 24)
    ac.setSize(b_showGBars      , 65, 24)
    ac.setSize(b_Temp           , 65, 24)
    ac.setSize(b_Press          , 65, 24)
    ac.setSize(b_saveResults    , 85, 24)
    ac.setSize(b_saveResultsNow , 85, 18)

    ac.setSize(b_transpFGUp     , 30, 40)
    ac.setSize(b_transpFGDn     , 30, 40)
    ac.setSize(b_transpHLUp     , 30, 40)
    ac.setSize(b_transpHLDn     , 30, 40)

    ac.setSize(b_arcade     ,  50, 40)
    ac.setPosition(b_arcade , -160,  210)

    ac.setPosition(b_gforceDec     ,   0, -45)
    ac.setPosition(b_gforceInc     ,  25, -45)
    ac.setPosition(b_smoothValueDn ,  60, -45)
    ac.setPosition(b_smoothValueUp ,  85, -45)
    ac.setPosition(b_TrailDn       , 120, -45)
    ac.setPosition(b_TrailUp       , 145, -45)
    ac.setPosition(b_TrailSmoothDn , 210, -45)
    ac.setPosition(b_TrailSmoothUp , 235, -45)
    ac.setPosition(b_vertToggle    , 270, -45)
    ac.setPosition(b_doResetOnFFB  , 320, -45)

    ac.setPosition(b_transpTxDn    , 145,-100)
    ac.setPosition(b_transpTxUp    , 180,-100)
    ac.setPosition(b_color         , 225,-100)
    ac.setPosition(b_texid         , 270,-100)
    ac.setPosition(b_reset         , 320,-100)
    ac.setPosition(b_SizeDec       ,   0,-100)
    ac.setPosition(b_SizeInc       ,  25,-100)
    ac.setPosition(b_transpBGDn    ,  60,-100)
    ac.setPosition(b_transpBGUp    ,  95,-100)

    ac.setPosition(b_transpGDn     , 145,-150)
    ac.setPosition(b_transpGUp     , 180,-150)
    ac.setPosition(b_histDotSizeInc, 230,-150)
    ac.setPosition(b_histDotSizeDec, 265,-150)
    ac.setPosition(b_DotSizeInc    , 320,-150)
    ac.setPosition(b_DotSizeDec    , 355,-150)

    ac.setPosition(b_saveResults   , -80, -150)
    ac.setPosition(b_saveResultsNow, -80, -125)
    ac.setPosition(b_Press         , -80, -100)
    ac.setPosition(b_Temp          , -80,  -75)
    ac.setPosition(b_showLabels    , -80,  -40)
    ac.setPosition(b_showTyres     , -80,  -15)
    ac.setPosition(b_showPedals    , -80,   10)
    ac.setPosition(b_showFFB       , -80,   35)
    ac.setPosition(b_showGForce    , -80,   70)
    ac.setPosition(b_showGBars     , -80,   95)
    ac.setPosition(b_showTraction  , -80,  130)
    ac.setPosition(b_transpFGDn    , -80,  165)
    ac.setPosition(b_transpFGUp    , -45,  165)
    ac.setPosition(b_transpHLDn    ,-165,  165)
    ac.setPosition(b_transpHLUp    ,-130,  165)

    ac.setPosition(b_transphistDn  ,20,  -150)
    ac.setPosition(b_transphistUp  ,70,  -150)

    ac.setPosition(b_Green         , -90, 210)
    ac.setPosition(b_Yellow        , -90, 230)
    ac.setPosition(b_Orange        , -90, 250)
    ac.setPosition(b_Red           , -90, 270)
    ac.setPosition(b_Blue          , -90, 290)
    ac.setSize(    b_Green         ,  80, 19)
    ac.setSize(    b_Yellow        ,  80, 19)
    ac.setSize(    b_Orange        ,  80, 19)
    ac.setSize(    b_Red           ,  80, 19)
    ac.setSize(    b_Blue          ,  80, 19)

    ac.setFontAlignment(b_Green   , 'right')
    ac.setFontAlignment(b_Yellow  , 'right')
    ac.setFontAlignment(b_Orange  , 'right')
    ac.setFontAlignment(b_Red     , 'right')
    ac.setFontAlignment(b_Blue    , 'right')

    ac.setFontAlignment(b_showTraction          , 'right')
    ac.setFontAlignment(b_showGForce          , 'right')
    ac.setFontAlignment(b_showTyres          , 'right')
    ac.setFontAlignment(b_showPedals          , 'right')
    ac.setFontAlignment(b_showFFB          , 'right')
    ac.setFontAlignment(b_showLabels          , 'right')
    ac.setFontAlignment(b_showGBars          , 'right')
    ac.setFontAlignment(b_Temp          , 'right')
    ac.setFontAlignment(b_Press          , 'right')

    #####################################################

    ac.addOnClickedListener(b_histDotSizeInc, apphistDotSizeDn)
    ac.addOnClickedListener(b_histDotSizeDec, apphistDotSizeUp)
    ac.addOnClickedListener(b_DotSizeInc, appDotSizeDn)
    ac.addOnClickedListener(b_DotSizeDec, appDotSizeUp)

    ac.addOnClickedListener(b_SizeDec, onSizeDec)
    ac.addOnClickedListener(b_SizeInc, onSizeInc)
    ac.addOnClickedListener(b_transpBGUp, appBGTransparencyUp)
    ac.addOnClickedListener(b_transpBGDn, appBGTransparencyDn)

    ac.addOnClickedListener(b_gforceDec, onGforceDec)
    ac.addOnClickedListener(b_gforceInc, onGforceInc)
    ac.addOnClickedListener(b_reset, onReset)
    ac.addOnClickedListener(b_doResetOnFFB, ondoResetOnFFB)
    ac.addOnClickedListener(b_vertToggle, onvertToggle)
    ac.addOnClickedListener(b_color, onColor)
    ac.addOnClickedListener(b_texid, onTexid)

    ac.addOnClickedListener(b_smoothValueDn, appsmoothValueDn)
    ac.addOnClickedListener(b_smoothValueUp, appsmoothValueUp)
    ac.addOnClickedListener(b_TrailDn, appTrailDn)
    ac.addOnClickedListener(b_TrailUp, appTrailUp)
    ac.addOnClickedListener(b_TrailSmoothDn, appTrailSmoothDn)
    ac.addOnClickedListener(b_TrailSmoothUp, appTrailSmoothUp)
    ac.addOnClickedListener(b_transpTxUp, appTxTransparencyUp)
    ac.addOnClickedListener(b_transpTxDn, appTxTransparencyDn)
    ac.addOnClickedListener(b_transpFGUp, appFGTransparencyUp)
    ac.addOnClickedListener(b_transpFGDn, appFGTransparencyDn)
    ac.addOnClickedListener(b_transpHLUp, appHLTransparencyUp)
    ac.addOnClickedListener(b_transpHLDn, appHLTransparencyDn)

    ac.addOnClickedListener(b_transpGUp, appGTransparencyUp)
    ac.addOnClickedListener(b_transpGDn, appGTransparencyDn)

    ac.addOnClickedListener(b_transphistUp, apphistTransparencyUp)
    ac.addOnClickedListener(b_transphistDn, apphistTransparencyDn)

    ac.addOnClickedListener(b_arcade    , onArcadeToggle)

    ac.addOnClickedListener(b_showGForce, onShowGForces)
    ac.addOnClickedListener(b_showTyres , onShowTyres)
    ac.addOnClickedListener(b_showPedals, onShowPedals)
    ac.addOnClickedListener(b_showTraction, onShowTraction)
    ac.addOnClickedListener(b_showFFB, onShowFFB)
    ac.addOnClickedListener(b_showLabels, onShowLabels)
    ac.addOnClickedListener(b_showGBars, onShowMaxOnly)
    ac.addOnClickedListener(b_Temp, onTemp)
    ac.addOnClickedListener(b_Press, onPress)
    ac.addOnClickedListener(b_saveResults, onsaveResults)
    ac.addOnClickedListener(b_saveResultsNow, onsaveResultsNow)

    ac.addOnClickedListener(b_Green , appToggleGreen   )
    ac.addOnClickedListener(b_Yellow, appToggleYellow  )
    ac.addOnClickedListener(b_Orange, appToggleOrange  )
    ac.addOnClickedListener(b_Red   , appToggleRed     )
    ac.addOnClickedListener(b_Blue  , appToggleBlue    )


    ac.addOnClickedListener     (appWindow, on_click_app_window)
    ac.addOnAppActivatedListener(appWindow, appOnActivated)
    # ac.addOnAppDismissedListener(appWindow, appOnClosed)
    ac.addRenderCallback        (appWindow, onFormRender)
  except:
    ac.log('G-Force error: ' + traceback.format_exc() )

  onReset()
  appResize()
  appHideButtons()
  return "GForce"

def onsaveResults(*args):
  global saveResults
  saveResults = not saveResults
  on_click_app_window()

def apphistTransparencyUp(*args):
  global ghistT
  ghistT += 10
  if ghistT>100:
    ghistT=100
  on_click_app_window()

def apphistTransparencyDn(*args):
  global ghistT
  ghistT -= 10
  if ghistT<0:
    ghistT=0
  on_click_app_window()

def appResizeMain(wl,hl):
  global wmain, hmain
  wmain=int(wl)
  hmain=int(hl)

def appResize():
  global gSizeGforce, b_SizeDec, b_SizeInc, appWindow, fontSize, showGForce, showLabels, showTyres, showPedals, showTraction, l_gforce, gforce_fac, showFFB, showGBars
  global showHeader, box_w, box_w2, box_h, box_h2, offset, top, gOpacityBG, gOpacityFG, gOpacityTx
  global boffset, bar_width, b_reset, b_doResetOnFFB, DoResetOnUSERFFBChange
  global rtIndexGF, rtIndex0, PNGmultGF, myImageGF
  global wmain, hmain
  global gforce_x_act, gforce_y_act, gforce_z_act

  try:
    ac.drawBorder(appWindow, 0)
    if showHeader == 0:
      top=0
      ac.setTitle(appWindow, "")
    else:
      top = 25
      ac.setTitle(appWindow, "GForce")

    # text box size
    fontSize = int(float(gSizeGforce/7.0))
    offset = fontSize
    box_w  = fontSize*2  # *4/2
    box_w2 = (fontSize*5)/2
    box_h  = fontSize*2+fontSize/2
    box_h2 = fontSize*3+fontSize/2

    # x offset for the tyres
    if showGForce and showTyres:
      offset = gSizeGforce*2
    if not showGForce and not showTyres:
      top = fontSize*2.5
    boffset = -30
    bar_width = box_w2*4.1
    if not showTyres and showGForce:
      boffset = gSizeGforce/6
      bar_width = box_w*2+gSizeGforce*1.2
    if not showTyres and not showGForce:
      boffset = -1*(2*box_h+12+gSizeGforce)

    lastWmain = wmain
    if not showTyres and showGForce:
      if showPedals:
        if showFFB:
          appResizeMain(offset+gSizeGforce*1.9, top+boffset+gSizeGforce*2.2) # show the pedals under gforce plot
        else:
          appResizeMain(offset+gSizeGforce*1.9, top+boffset+gSizeGforce*2) # show the pedals under gforce plot
      else:
        appResizeMain(offset+gSizeGforce*1.9, top+gSizeGforce*2)
    elif showTyres and not showGForce and not showPedals:
      appResizeMain(offset+box_w2*4.5, top+2*box_h+12+gSizeGforce)
    elif showPedals and not showTyres and not showGForce:
      if showFFB:
        appResizeMain(offset+gSizeGforce*1.9, top+60)
      else:
        appResizeMain(offset+gSizeGforce*1.9, top+40)
    else:
      appResizeMain(offset+gSizeGforce*1.5, gSizeGforce*2)
      wmain = int(hmain+4*gSizeGforce/100)   #top+gSizeGforce*2+1

    PNGmultGF = myImageGF.size[0] / wmain
    # ac.log(str(wmain) + '         ' + str( hmain) )
    # ac.log('pngmult: ' + str(PNGmultGF))
    #  236                232
    #  348                348
    #  2.942528735632184 4.338983050847458



    if showTyres and showGForce:
      ac.setSize(appWindow, offset+gSizeGforce*1.5, hmain)
    else:
      if gOpacityBG==0:
        ac.setSize(appWindow, wmain, hmain/2)
      else:
        ac.setSize(appWindow, wmain, hmain)

    if (lastWmain != wmain):
      gforce_x_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
      gforce_y_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
      gforce_z_act = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0 , 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

      if bCSPActive:
        if rtIndexGF>-1:
          ### delete mem texture
          ac.ext_disposeRenderTarget(rtIndexGF)
          ac.ext_disposeRenderTarget(rtIndex0)
          rtIndex0 = -1
          rtIndexGF = -1
        #### returns texture index, but also this number can be used to draw things to
        rtIndexGF = ac.ext_createRenderTarget(wmain, wmain, False)
        rtIndex0 = ac.ext_createRenderTarget(200, 200, False) #

        # prepare blending image to fade out stuff, black almost transparent image
        ac.ext_bindRenderTarget(rtIndex0)
        #ac.glColor4f(0,0,0,0.1)
        ac.glColor4f(0.2,0.2,0.2,0.1)
        ac.glBegin(acsys.GL.Quads)
        ac.glVertex2f(0,0)
        ac.glVertex2f(0,200)
        ac.glVertex2f(200,200)
        ac.glVertex2f(200,0)
        ac.glEnd()
        ac.ext_restoreRenderTarget()


    # g forces
    for idx in range(6):
      ac.setVisible(l_gforce[idx], showLabels and showGForce)
    if showGForce:
      ac.setPosition(l_gforce[0], 0                    +box_w/3         , top+box_h/2+gSizeGforce*0.1)
      ac.setPosition(l_gforce[1], box_w+ 5+gSizeGforce  +box_w/3        , top+box_h/2+gSizeGforce/2.2)
      ac.setPosition(l_gforce[2], box_w+ 5+gSizeGforce/2-box_w/2        , top+box_h+gSizeGforce)
      ac.setPosition(l_gforce[3], gSizeGforce*1.6                       , top+gSizeGforce/20)
      ac.setPosition(l_gforce[4], gSizeGforce*1.6                       , top+gSizeGforce/2)  # top-25
      ac.setPosition(l_gforce[5], box_w+10+gSizeGforce/2-box_w/2+box_w+5, top+box_h+10+gSizeGforce) # +40

    for idx in range(7):
      ac.setFontAlignment(l_gforce[idx], "right")
      ac.setFontColor(l_gforce[idx],1,1,1,gOpacityTx/100)
      if idx!=5:
        ac.setFontSize(l_gforce[idx], fontSize*0.85)
        ac.setSize(l_gforce[idx], box_w, box_h)
      else:
        ac.setFontSize(l_gforce[idx], fontSize*0.75)
        ac.setSize(l_gforce[idx], box_w/3*2, box_h/4*3)
    ac.setFontAlignment(l_gforce[0], "left")

    ac.setFontSize(l_gforce[4], fontSize*0.65)

    if showPedals and not showTyres and not showGForce:
      ac.setPosition(l_gforce[6], gSizeGforce*1.2, 1)
    elif showGForce:
      if showTyres:
        ac.setPosition(l_gforce[6], offset+gSizeGforce*1.1, gSizeGforce*1.175)
      else:
        ac.setPosition(l_gforce[6], gSizeGforce*1.6, gSizeGforce*1.3)
    else:
      if showTyres:
        ac.setPosition(l_gforce[6], gSizeGforce*1.2, gSizeGforce*1.2)
      else:
        ac.setPosition(l_gforce[6], gSizeGforce*1.2, top)
      ac.setFontSize(l_gforce[6], fontSize*0.75)


    if showFFB:
      ac.setVisible(l_gforce[6], 1)
      if gforce_max[6]<=1.0:
        ac.setFontColor(l_gforce[6],1,1,1,gOpacityTx/100)
      else:
        ac.setFontColor(l_gforce[6],1,0.5,0.5,gOpacityTx/100)
    else:
      ac.setVisible(l_gforce[6], 0)

    if showLabels:
      ac.setVisible(l_gforce[4], 1)
      ac.setVisible(l_gforce[5], 1)
    else:
      ac.setVisible(l_gforce[4], 0)
      ac.setVisible(l_gforce[5], 0)

    ac.setFontAlignment(l_tyre[0], "right")
    ac.setFontAlignment(l_tyre[2], "right")
    ac.setFontAlignment(l_tyre[1], "left")
    ac.setFontAlignment(l_tyre[3], "left")
    # tyres
    for idx in range(4):
      ac.setVisible(l_tyre[idx], showLabels)
    #  x_left  = offset+gSizeGforce*0.5
    #  x_right = offset+gSizeGforce*0.65

    if showTyres:
      #ac.setPosition(l_tyre[0], gSizeGforce*0.1 + offset                       , top)
      #ac.setPosition(l_tyre[1], gSizeGforce*0.1 + offset+box_w2+50+fontSize*0.5, top)
      #ac.setPosition(l_tyre[2], gSizeGforce*0.1 + offset                       , top+box_h2+15)
      #ac.setPosition(l_tyre[3], gSizeGforce*0.1 + offset+box_w2+50+fontSize*0.5, top+box_h2+15)
      ac.setPosition(l_tyre[0], offset+gSizeGforce*0.10, top)
      ac.setPosition(l_tyre[1], offset+gSizeGforce*0.5+60, top)
      ac.setPosition(l_tyre[2], offset+gSizeGforce*0.10, top+box_h2+15)
      ac.setPosition(l_tyre[3], offset+gSizeGforce*0.5+60, top+box_h2+15)
      for idx in range(4):
        ac.setFontSize(l_tyre[idx], fontSize*0.9)
        ac.setSize(l_tyre[idx], box_w2, box_h2)
    else:
      ac.setPosition(l_tyre[0], gSizeGforce*0.1 + offset          , -20000)
      ac.setPosition(l_tyre[1], gSizeGforce*0.1 + offset+box_w2+50, -20000)
      ac.setPosition(l_tyre[2], gSizeGforce*0.1 + offset          , -20000)
      ac.setPosition(l_tyre[3], gSizeGforce*0.1 + offset+box_w2+50, -20000)
  except:
    ac.log('error: ' + traceback.format_exc() )

  #ac.setFontSize(b_vertToggle, fontSize)
  on_click_app_window()

  ### debug save settings
  ### acShutdown()

def on_click_app_window(*args):
  global texid, b_texid, gOpacityBG, gOpacityFG, gOpacityTx, bActiveTimer, fTimer, b_color, b_SizeDec, gSizeGforce, b_vertToggle, b_transpBGDn, b_transpBGUp, b_transpFGDn, b_transpFGUp, b_transpTxUp, b_transpTxDn, showGForce, showTyres, showPedals, showLabels, b_arcade
  global b_showPedals, b_showTraction, b_transpTxDn, b_showGForce, b_showTyres, b_showLabels, histCount, b_TrailDn, b_TrailUp, b_TrailSmoothDn, b_TrailSmoothUp, histVisi, b_smoothValueDn, b_smoothValueUp, smoothValue, b_Temp, b_Press, b_showFFB, showFFB
  global b_Press, b_Temp, TempID, PressID, showGBars, b_showGBars, b_gforceDec, b_gforceInc, base_gforce_fac, b_doResetOnFFB
  global b_Green, b_Yellow, b_Orange, b_Red, b_Blue
  global bGreen, bYellow, bOrange, bRed, bBlue, showArcade, gforce_fac, bScaleFixed
  global gOpacityHL, b_transpHLUp, b_transpHLDn, b_reset, DoResetOnUSERFFBChange
  global b_transpGUp, b_transpGDn, gOpacityG
  global b_transphistUp, b_transphistDn
  global gSizeSub, gOpacityBGSub
  global appWindow, saveResults, b_saveResults, b_saveResultsNow
  global b_histDotSizeDec, b_histDotSizeInc, histDotSize
  global b_DotSizeDec, b_DotSizeInc, DotSize

  bActiveTimer = True
  fTimer = 5.0
  ac.setText(b_gforceDec     , '- ' + str(round(base_gforce_fac,1)) + '\n     MAX g')
  # if bScaleFixed:
  #ac.setText(b_gforceDec     , '- '   + str(round(base_gforce_fac,1)) + '\n     MAX g' +
  #                            '\n '   + str(round(gforce_fac,1)) + '\n     MAX g')
  ac.setIconPosition(appWindow, -40, 0)

  ac.setText(b_reset, "reset\nmax g & ffb")
  if DoResetOnUSERFFBChange:
    ac.setText(b_doResetOnFFB, "numpad +/-\nreset: ON")
  else:
    ac.setText(b_doResetOnFFB, "numpad +/-\nreset: off")

  ac.setText(b_smoothValueDn  , '-  '  + str(int(smoothValue)) + '\nsmooth')
  ac.setText(b_SizeDec        , '  - ' + str(int(gSizeGforce))  + '\n     size px')
  ac.setText(b_transpBGDn     , '-  '  + str(int(gOpacityBG))  + '%\n BackGrnd')
  ac.setText(b_transpTxDn     , '- '   + str(int(gOpacityTx))  + '%\ntextOpac.')
  ac.setText(b_transpFGDn     , '- '   + str(int(gOpacityFG))  + '%\ncirc Opac.')
  ac.setText(b_transpHLDn     , '- '   + str(int(gOpacityHL))  + '%\nhighlights')
  ac.setText(b_transpGDn      , '  - ' + str(int(gOpacityG))   + '%\n       BG circles')
  ac.setText(b_transphistDn   , '  - ' + str(int(ghistT))      + '%\n           historyTransp')
  ac.setText(b_TrailDn        , '- '   + str(int(histCount))  + '\n length')
  ac.setText(b_TrailSmoothDn  , ' - '  + str(int(histVisi))   + '%\nalpha')
  ac.setText(b_histDotSizeInc , '  - ' + str(round(histDotSize,1))      + 'px\n       hist dot-size')
  ac.setText(b_DotSizeInc     , '  - ' + str(round(DotSize,1))      + 'px\n       dot-size')
  if showArcade:
    ac.setText(b_arcade        , 'arcade\nON')
  else:
    ac.setText(b_arcade        , 'arcade\noff')

  ac.setText(b_Green , "tyreSlip "  + str(int(bGreen) ))
  ac.setText(b_Yellow, "Mz "        + str(int(bYellow)))
  ac.setText(b_Orange, "SlipRatio " + str(int(bOrange)))
  ac.setText(b_Red   , "NDslip "    + str(int(bRed)   ))
  ac.setText(b_Blue  , "SlipAngle " + str(int(bBlue)  ))

  if zForce==True:
    if centeredZForce==True:
      ac.setText(b_vertToggle, "2/2\nGz")
    else:
      ac.setText(b_vertToggle, "1/2\nGz")
  else:
    ac.setText(b_vertToggle, "0/2\nGz")
  ac.setText(b_color         , str(gColor)+'/2\ncol')
  ac.setText(b_texid         , str(texid) + '/6\ngrid')

  if showTraction:
    ac.setText(b_showTraction,'tractCirc 1')
  else:
    ac.setText(b_showTraction,'tractCirc 0')
  if showGForce:
    ac.setText(b_showGForce,'gForce 1')
  else:
    ac.setText(b_showGForce,'gForce 0')
  if showPedals:
    ac.setText(b_showPedals,'pedals 1')
  else:
    ac.setText(b_showPedals,'pedals 0')
  if showTyres:
    ac.setText(b_showTyres,'tyres 1')
  else:
    ac.setText(b_showTyres,'tyres 0')
  if showLabels:
    ac.setText(b_showLabels,'text 1')
  else:
    ac.setText(b_showLabels,'text 0')
  if saveResults:
    ac.setText(b_saveResults,"save png's 1")
  else:
    ac.setText(b_saveResults,"save png's 0")
  if showGBars:
    ac.setText(b_showGBars,'g-bars 1')
  else:
    ac.setText(b_showGBars,'g-bars 0')
  if showFFB:
    ac.setText(b_showFFB,'ffb 1')
  else:
    ac.setText(b_showFFB,'ffb 0')
  if TempID:
    ac.setText(b_Temp,'Farenh.')
  else:
    ac.setText(b_Temp,'Celcius')
  if PressID:
    ac.setText(b_Press,'psi')
  else:
    ac.setText(b_Press,'bar')
  if showTraction:
    ac.setVisible(b_transpFGUp, 1)
    ac.setVisible(b_transpFGDn, 1)
    ac.setVisible(b_transpHLUp, 1)
    ac.setVisible(b_transpHLDn, 1)
    ac.setVisible(b_arcade    , 1)
    ac.setVisible(b_Green     , 1)
    ac.setVisible(b_Yellow    , 1)
    ac.setVisible(b_Orange    , 1)
    ac.setVisible(b_Red       , 1)
    ac.setVisible(b_Blue      , 1)
  else:
    ac.setVisible(b_transpHLUp, 0)
    ac.setVisible(b_transpHLDn, 0)
    ac.setVisible(b_transpFGUp, 0)
    ac.setVisible(b_transpFGDn, 0)
    ac.setVisible(b_arcade    , 0)
    ac.setVisible(b_Green     , 0)
    ac.setVisible(b_Yellow    , 0)
    ac.setVisible(b_Orange    , 0)
    ac.setVisible(b_Red       , 0)
    ac.setVisible(b_Blue      , 0)
  ac.setVisible(b_transpTxUp, 1)
  ac.setVisible(b_transpTxDn, 1)
  ac.setVisible(b_transpGUp, 1)
  ac.setVisible(b_transpGDn, 1)
  ac.setVisible(b_transphistUp, 1)
  ac.setVisible(b_transphistDn, 1)
  ac.setVisible(b_showGForce, 1)
  ac.setVisible(b_showPedals, 1)
  ac.setVisible(b_showTraction, 1)
  ac.setVisible(b_showTyres, 1)
  ac.setVisible(b_showFFB, 1)
  ac.setVisible(b_showLabels, 1)
  ac.setVisible(b_saveResults, 1)
  ac.setVisible(b_saveResultsNow, 1)
  ac.setVisible(b_showGBars, 1)
  ac.setVisible(b_gforceDec, 1)
  ac.setVisible(b_gforceInc, 1)
  ac.setVisible(b_Press, 1)
  ac.setVisible(b_Temp, 1)
  ac.setVisible(b_vertToggle, 1)
  ac.setVisible(b_smoothValueDn, 1)
  ac.setVisible(b_smoothValueUp, 1)
  ac.setVisible(b_TrailUp, 1)
  ac.setVisible(b_TrailDn, 1)
  ac.setVisible(b_TrailSmoothDn, 1)
  ac.setVisible(b_TrailSmoothUp, 1)
  ac.setVisible(b_color, 1)
  ac.setVisible(b_reset, 1)
  ac.setVisible(b_doResetOnFFB, 1)
  ac.setVisible(b_texid, 1)
  ac.setVisible(b_transpBGUp, 1)
  ac.setVisible(b_transpBGDn, 1)
  ac.setVisible(b_SizeDec, 1)
  ac.setVisible(b_SizeInc, 1)
  ac.setVisible(b_histDotSizeDec, 1)
  ac.setVisible(b_histDotSizeInc, 1)
  ac.setVisible(b_DotSizeDec, 1)
  ac.setVisible(b_DotSizeInc, 1)

def appDrawTyreBar(cval, temp, x, y, width=10, height=10):
  global gColor
  if temp>70:
    ac.glColor4f(0.5+cval/3*2, 1-cval*1.5, 0.5-cval*0.75, 1)
  else:
    ac.glColor4f(0.5-cval, 1-cval*2, 0.5+cval, 1)
  ac.glQuad(x, y, width, height)

def appSetFontColorTyres(l_tyre, cval, temp):
  global gColor
  if gColor==0:
    ac.setFontColor(l_tyre, 1, 1, 1, 1)
  else:
    if temp>70:
      ac.setFontColor(l_tyre, 0.5+cval/3*2, 1-cval*1.5, 0.5-cval*0.75, 1)
    else:
      ac.setFontColor(l_tyre, 0.5-cval, 1-cval*2, 0.5+cval, 1)

def appHideButtons():
  global b_vertToggle, b_transpBGUp, b_transpBGDn, b_transpFGDn, b_arcade, b_transpFGUp, b_transpTxDn, b_transpTxUp, b_reset, b_doResetOnFFB, b_color, b_SizeDec, b_SizeInc, b_TrailDn, b_TrailUp, b_smoothValueDn, b_smoothValueUp, b_showPedals, b_showTraction, b_gforceDec, b_gforceInc, b_saveResults
  global b_Green, b_Yellow, b_Orange, b_Red, b_Blue, b_transpHLUp, b_transpHLDn, b_transpGUp, b_transpGDn, b_saveResultsNow
  global b_transphistUp, b_transphistDn, appWindow
  global b_DotSizeDec, b_DotSizeInc, DotSize
  if showHeader == 0:
    ac.setTitle(appWindow, "")

  ac.setIconPosition(appWindow, -10000, -10000)
  ac.setVisible(b_histDotSizeDec, 0)
  ac.setVisible(b_histDotSizeInc, 0)
  ac.setVisible(b_DotSizeDec, 0)
  ac.setVisible(b_DotSizeInc, 0)
  ac.setVisible(b_transphistUp, 0)
  ac.setVisible(b_transphistDn, 0)
  ac.setVisible(b_Green     , 0)
  ac.setVisible(b_Yellow    , 0)
  ac.setVisible(b_Orange    , 0)
  ac.setVisible(b_Red       , 0)
  ac.setVisible(b_Blue      , 0)
  ac.setVisible(b_arcade    , 0)
  ac.setVisible(b_vertToggle, 0)
  ac.setVisible(b_gforceDec , 0)
  ac.setVisible(b_gforceInc , 0)
  ac.setVisible(b_transpBGUp, 0)
  ac.setVisible(b_transpBGDn, 0)
  ac.setVisible(b_transpFGUp, 0)
  ac.setVisible(b_transpFGDn, 0)
  ac.setVisible(b_transpHLUp, 0)
  ac.setVisible(b_transpHLDn, 0)
  ac.setVisible(b_transpTxUp, 0)
  ac.setVisible(b_transpTxDn, 0)
  ac.setVisible(b_transpGUp, 0)
  ac.setVisible(b_transpGDn, 0)
  ac.setVisible(b_TrailUp   , 0)
  ac.setVisible(b_TrailDn   , 0)
  ac.setVisible(b_TrailSmoothDn, 0)
  ac.setVisible(b_TrailSmoothUp, 0)
  ac.setVisible(b_smoothValueDn, 0)
  ac.setVisible(b_smoothValueUp, 0)
  ac.setVisible(b_color, 0)
  ac.setVisible(b_reset, 0)
  ac.setVisible(b_doResetOnFFB, 0)
  ac.setVisible(b_SizeDec, 0)
  ac.setVisible(b_SizeInc, 0)
  ac.setVisible(b_showGForce, 0)
  ac.setVisible(b_showPedals, 0)
  ac.setVisible(b_showTraction, 0)
  ac.setVisible(b_showTyres, 0)
  ac.setVisible(b_showLabels, 0)
  ac.setVisible(b_saveResults, 0)
  ac.setVisible(b_saveResultsNow, 0)
  ac.setVisible(b_showGBars, 0)
  ac.setVisible(b_showFFB, 0)
  ac.setVisible(b_Temp, 0)
  ac.setVisible(b_Press, 0)
  ac.setVisible(b_texid, 0)

def appsmoothValueDn(*args):
  global smoothValue
  smoothValue -= 1
  if smoothValue<0:
    smoothValue=0
  appResize()
def appsmoothValueUp(*args):
  global smoothValue
  smoothValue += 1
  if smoothValue>50:
    smoothValue=50
  appResize()
def onShowGForces(*args):
  global showGForce
  showGForce=not showGForce
  appResize()
def onArcadeToggle(*args):
  global showArcade
  showArcade=not showArcade
  appResize()
def onShowTyres(*args):
  global showTyres
  showTyres=not showTyres
  appResize()
def onShowPedals(*args):
  global showPedals
  showPedals=not showPedals
  appResize()
def onShowTraction(*args):
  global showTraction
  showTraction=not showTraction
  appResize()

def appToggleGreen(*args):
  global bGreen
  bGreen = not bGreen
  on_click_app_window()
def appToggleYellow(*args):
  global bYellow
  bYellow = not bYellow
  on_click_app_window()
def appToggleOrange(*args):
  global bOrange
  bOrange = not bOrange
  on_click_app_window()
def appToggleRed(*args):
  global bRed
  bRed = not bRed
  on_click_app_window()
def appToggleBlue(*args):
  global bBlue
  bBlue = not bBlue
  on_click_app_window()

def onShowFFB(*args):
  global showFFB
  showFFB=not showFFB
  appResize()
def onShowLabels(*args):
  global showLabels
  showLabels=not showLabels
  appResize()
def onShowMaxOnly(*args):
  global showGBars
  showGBars=not showGBars
  appResize()
def onTemp(*args):
  global TempID
  TempID += 1
  if TempID >= 2:
    TempID = 0
  appResize()
def onPress(*args):
  global PressID
  PressID += 1
  if PressID >= 2:
    PressID = 0
  appResize()
def onTexid(*args):
  global texture_gforce, texid, texid0, texid1, texid2, texid3, texid4, texid5
  texid+=1
  if texid>6:
    texid=0
  if texid==0:
    texture_gforce = texid0
  elif texid==1:
    texture_gforce = texid1
  elif texid==2:
    texture_gforce = texid2
  elif texid==3:
    texture_gforce = texid3
  elif texid==4:
    texture_gforce = texid4
  elif texid>=5:
    texture_gforce = texid5
  appResize()

def appTrailDn(*args):
  global histCount, lastXYZ, lastXY, maxHistCount
  if histCount>50:
    histCount -= 50
  elif histCount>10:
    histCount -= 10
  elif histCount>1:
    histCount -= 1
  else:
    histCount=0
  lastXYZ    = [[111.0,111.0,111.0] * maxHistCount for i in range(maxHistCount)]
  lastXY     = [[111.0,111.0      ] * maxHistCount for i in range(maxHistCount)]
  appResize()

def appTrailUp(*args):
  global histCount, lastXYZ, lastXY, maxHistCount
  if histCount<10:
    histCount += 1
  elif histCount<50:
    histCount += 10
  elif histCount<maxHistCount:
    histCount += 50
  else:
    histCount=maxHistCount
  lastXYZ    = [[111.0,111.0,111.0] * maxHistCount for i in range(maxHistCount)]
  lastXY     = [[111.0,111.0      ] * maxHistCount for i in range(maxHistCount)]
  appResize()

def appTrailSmoothDn(*args):
  global histVisi
  if histVisi>0:
    histVisi -= 2
  else:
    histVisi=0
  appResize()

def appTrailSmoothUp(*args):
  global histVisi
  if histVisi<100:
    histVisi += 2
  else:
    histVisi=100
  appResize()

def appOnActivated(*args):
  on_click_app_window()

def onColor(*args):
  global gColor
  if gColor<2:
    gColor+=1
  else:
    gColor=0
  appResize()

def appBGTransparencyUp(*args):
  global gOpacityBG
  gOpacityBG += 10
  if gOpacityBG>100:
    gOpacityBG = 100
  appResize()
def appBGTransparencyDn(*args):
  global gOpacityBG
  gOpacityBG -= 10
  if gOpacityBG<0:
    gOpacityBG = 0
  appResize()

def appFGTransparencyUp(*args):
  global gOpacityFG
  gOpacityFG += 10
  if gOpacityFG>200:
    gOpacityFG=200
  appResize()
def appFGTransparencyDn(*args):
  global gOpacityFG
  gOpacityFG -= 10
  if gOpacityFG<0:
    gOpacityFG=0
  appResize()

def appHLTransparencyUp(*args):
  global gOpacityHL
  if  gOpacityHL<400:
    gOpacityHL += 10
  if  gOpacityHL>400:
    gOpacityHL=400
  appResize()
def appHLTransparencyDn(*args):
  global gOpacityHL
  if  gOpacityHL>0:
    gOpacityHL -= 10
  if  gOpacityHL<0:
    gOpacityHL=0
  appResize()

def appTxTransparencyUp(*args):
  global gOpacityTx
  if gOpacityTx<100:
    gOpacityTx += 5
  if gOpacityTx>100:
    gOpacityTx=100
  appResize()
def appTxTransparencyDn(*args):
  global gOpacityTx
  if gOpacityTx>0:
    gOpacityTx -= 5
  if gOpacityTx<0:
    gOpacityTx=0
  appResize()

def appGTransparencyUp(*args):
  global gOpacityG
  if gOpacityG<100:
    gOpacityG += 5
  if gOpacityG>100:
    gOpacityG=100
  appResize()
def appGTransparencyDn(*args):
  global gOpacityG
  if gOpacityG>0:
    gOpacityG -= 5
  if gOpacityG<0:
    gOpacityG=0
  appResize()

def onvertToggle(*args):
  global b_vertToggle, zForce, centeredZForce
  if not zForce:
    zForce         = True
    centeredZForce = False
    ac.setText(b_vertToggle,'z1')
  else:
    if not centeredZForce:
      zForce         = True
      centeredZForce = True
      ac.setText(b_vertToggle,'z2')
    else:
      zForce         = False
      centeredZForce = False
      ac.setText(b_vertToggle,'z0')
  appResize()

def onSizeDec(dummy, variable):
  global gSizeGforce
  gSizeGforce = gSizeGforce - 5
  appResize()

def onSizeInc(dummy, variable):
  global gSizeGforce
  gSizeGforce = gSizeGforce + 5
  appResize()

################################

def drawBox(x, y, w, h, r, g, b):
  ac.glBegin(0)
  ac.glColor3f(r,g,b)
  ac.glVertex2f(x  , y)
  ac.glVertex2f(x+w, y)
  ac.glVertex2f(x-1, y+h)
  ac.glVertex2f(x+w, y+h)
  ac.glVertex2f(x+w, y)
  ac.glVertex2f(x+w, y+h)
  ac.glVertex2f(x  , y)
  ac.glVertex2f(x  , y+h)
  ac.glEnd()

def drawBoxa(x, y, w, h, r, g, b, a):
  ac.glColor4f(r,g,b,a)
  ac.glQuad(x, y, w, h )


def appDrawLineTriHori(r,g,b,a,x1,y1,x2,height=4):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Triangles)
  ac.glVertex2f(x1        ,y1-height/2)
  ac.glVertex2f(x2        ,y1)
  ac.glVertex2f(x1        ,y1+height/2)
  ac.glEnd()

def appDrawDot(r,g,b,a,x1,y1,sizeX,sizeYneg, sizeYpos, tex):
  global gSizeGforce
  ac.glColor4f(r,g,b,a)
  # ac.glQuadTextured(x1-sizeX/2*graphW, y1-sizeYneg/2*graphH, sizeX*graphW, sizeYpos*graphH, tex)
  ac.glQuadTextured(x1-sizeX/2*gSizeGforce, y1-sizeYneg*gSizeGforce/2, sizeX*gSizeGforce, (sizeYneg+sizeYpos)*gSizeGforce/2, tex)

def appDrawDotNS(r,g,b,a,x1,y1, sizeX, sizeYneg, sizeYpos, tex, div):
  global gSizeGforce
  ac.glColor4f(r,g,b,a)
  # ac.glQuadTextured(x1-sizeX/2*graphW, y1-sizeYneg/2*graphH, sizeX*graphW, sizeYpos*graphH, tex)
  ac.glQuadTextured(x1-sizeX*gSizeGforce/div*gSizeGforce/2, y1-sizeYneg*gSizeGforce/div*gSizeGforce/2, sizeX*gSizeGforce*2/div*gSizeGforce/2, (sizeYneg+sizeYpos)*gSizeGforce/div*gSizeGforce/2, tex)

def appDrawDotBothAxes(r,g,b,a,x1,y1,sizeXneg, sizeXpos, sizeYneg, sizeYpos, tex):
  global gSizeGforce
  ac.glColor4f(r,g,b,a)
  # ac.glQuadTextured(x1-sizeX/2*graphW, y1-sizeYneg/2*graphH, sizeX*graphW, sizeYpos*graphH, tex)
  ac.glQuadTextured(x1-sizeXneg/2*gSizeGforce, y1-sizeYneg/2*gSizeGforce, (sizeXneg/2+sizeXpos/2)*gSizeGforce, (sizeYneg/2+sizeYpos/2)*gSizeGforce, tex)


def appDrawDotNSPil(r,g,b,a,x1,y1,sizeX, sizeYneg, sizeYpos, img, img2):
  global gSizeGforce
  # ac.glColor4f(r,g,b,a)
  # # ac.glQuadTextured(x1-sizeX/2*graphW, y1-sizeYneg/2*graphH, sizeX*graphW, sizeYpos*graphH, tex)
  # ac.glQuadTextured(x1-sizeX/2*gSizeGforce, y1-sizeYneg/2*gSizeGforce, sizeX*gSizeGforce, (sizeYneg/2+sizeYpos/2)*gSizeGforce, tex)
  global gSizeGforce, wmain, PNGmultGF
  sz_halfH = int( sizeX*gSizeGforce*PNGmultGF)
  sz_halfV = int( (sizeYneg+sizeYpos)*gSizeGforce/2*PNGmultGF)
  newImg = img2.resize((sz_halfH, sz_halfV),
                        resample=Image.ANTIALIAS)
                        #resample=Image.Resampling.LANCZOS)
  newImg2 = ImageOps.colorize(newImg.convert("L"), (0,0,0), (r*255,g*255,b*255))
  mask = newImg.split()[-1]
  enh = ImageEnhance.Brightness(mask)
  mask = enh.enhance(a*2)
  newImg2.putalpha(mask)
  if sizeYpos==0:
    img.paste(newImg2,
              (int(PNGmultGF*wmain/2 - sizeX*gSizeGforce/2*PNGmultGF),
              int(PNGmultGF*wmain/2 - sizeYneg*gSizeGforce/2*PNGmultGF+3)),
              mask)
  else:
    img.paste(newImg2,
              (int(PNGmultGF*wmain/2 - sizeX*gSizeGforce/2*PNGmultGF),
              int(PNGmultGF*wmain/2 - sizeYneg*gSizeGforce/2*PNGmultGF)),
              mask)



def appDrawDotBothAxesPIL(r,g,b,a,x1,y1,sizeXneg, sizeXpos, sizeYneg, sizeYpos, img, img2):
  global gSizeGforce, wmain, PNGmultGF
  sz_halfH = int( (sizeXneg+sizeXpos)*gSizeGforce/2)
  sz_halfV = int( (sizeYneg+sizeYpos)*gSizeGforce/2)
  newImg = img2.resize((sz_halfH, sz_halfV),
                        resample=Image.ANTIALIAS)
                        #resample=Image.Resampling.LANCZOS)
  newImg2 = ImageOps.colorize(newImg.convert("L"), (0,0,0), (r*255,g*255,b*255))
  mask = newImg.split()[-1]
  enh = ImageEnhance.Brightness(mask)
  mask = enh.enhance(a*2)
  newImg2.putalpha(mask)

  img.paste(newImg2,
            (int(PNGmultGF*wmain/2 - sizeXneg*gSizeGforce/2),
             int(PNGmultGF*wmain/2 - sizeYneg*gSizeGforce/2)),
            mask)


########################################################################################################################################################
########################################################################################################################################################
########################################################################################################################################################
def DrawRotated(img, text, font, mult):
  # rotated
  txt=Image.new('L', (int(img.size[0]/2),int(img.size[0]/2)))
  d=ImageDraw.Draw(txt)
  d.text( (0, 0), text, font=font, fill=255)
  wtxt=txt.rotate(90, expand=0)
  img.paste( ImageOps.colorize(wtxt, (0,0,0), (255,255,184)), (int(380*mult),int(img.size[0]*0.425)), wtxt)





def runAsThread(sf):
  appSaveImages(sf)
  onReset()


def runSaveImagesThread(sf):
  global thread
  if not thread or not thread.is_alive():
    thread = threading.Thread(target=runAsThread, args=(sf,))
    thread.start()

def onsaveResultsNow(*args):
  runSaveImagesThread(time.strftime("_%Y-%m-%d %H_%M"))



def appSaveImages(postfix=''):
  global datagf, carName

  try:
    # paint in a cross
    canvasGF.rectangle( ( PNGmultGF*wmain/2-6, PNGmultGF*wmain/2-1, PNGmultGF*wmain/2+6, PNGmultGF*wmain/2+1 ), fill=(0,0,0) )
    canvasGF.rectangle( ( PNGmultGF*wmain/2-1, PNGmultGF*wmain/2-6, PNGmultGF*wmain/2+1, PNGmultGF*wmain/2+6 ), fill=(0,0,0) )
    canvasGF.rectangle( ( PNGmultGF*wmain/2-5, PNGmultGF*wmain/2  , PNGmultGF*wmain/2+5, PNGmultGF*wmain/2   ), fill=(255,255,255) )
    canvasGF.rectangle( ( PNGmultGF*wmain/2  , PNGmultGF*wmain/2-5, PNGmultGF*wmain/2  , PNGmultGF*wmain/2+5 ), fill=(255,255,255) )

    # draw some text while here
    # 'Lateral g-force vs Longit. g-force', font, mult)
    mult=myImageGF.size[0]/1024
    font = ImageFont.truetype('content/fonts/consola.ttf', size=int(25*mult))
    canvasGF.text((myImageGF.size[0]*0.01, myImageGF.size[0]-int(300*mult)),'Lateral g-force vs Longit. g-force'                        , font=font)
    # canvasGF.text((myImageGF.size[0]*0.01, myImageGF.size[0]-int(350*mult)),'Lateral g-force  VS '                                        , font=font)
    # DrawRotated(myImageGF, 'Longit. g-force', font, mult)
    font = ImageFont.truetype('content/fonts/consola.ttf', size=int(18*mult))
    canvasGF.text(               (20, myImageGF.size[0]*0.95 - 140*mult) ,"max g's"                                                       , font=font)
    canvasGF.text(               (20, myImageGF.size[0]*0.95 - 110*mult) ,"    displayed (x+y):    ±" + str(round(base_gforce_fac,2))     , font=font)
    canvasGF.text(               (20, myImageGF.size[0]*0.95 -  90*mult) ,"    left:                " + str(round(abs(gforce_max[0]),2))  , font=font)
    canvasGF.text(               (20, myImageGF.size[0]*0.95 -  70*mult) ,"    right:               " + str(round(abs(gforce_max[1]),2))  , font=font)
    canvasGF.text(               (20, myImageGF.size[0]*0.95 -  50*mult) ,"    on brakes:           " + str(round(abs(gforce_max[2]),2))  , font=font)
    canvasGF.text(               (20, myImageGF.size[0]*0.95 -  30*mult) ,"    on throttle:         " + str(round(abs(gforce_max[3]),2))  , font=font)
    font = ImageFont.truetype('content/fonts/consola.ttf', size=int(12*mult))
    canvasGF.text((20, myImageGF.size[0]*0.95 +  30),
        '|  ' + carName +  '  |  ' + ac.getTrackName(0)+ '  |  ' +
        "data points: " + str(int(datagf)) + '  |  ',
        font=font)

    # if showTraction and gOpacityFG > 0:
    if True:
      myImageGF_trac = Image.open('apps/python/GForce/gforce_blanc.png')
      # paint in traction overlays on PIL image
      ### draw all full traction circles
      myImageGF_trac.putalpha(0)
      myImageCircleN = Image.open("apps/python/GForce/circle_N.png")
      myImageCircleS = Image.open("apps/python/GForce/circle_S.png")
      wd = gSizeGforce
      if bBlue:
        # draw full blue overlay
        appDrawDotNSPil(0.35,0.35,1.0,0.5, wd, wd, max(maxG_XBLUneg, maxG_XBLUpos)/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUneg/gforce_fac*gSizeGforce/DivBlue,                                           0, myImageGF_trac, myImageCircleN )
        appDrawDotNSPil(0.35,0.35,1.0,0.5, wd, wd, max(maxG_XBLUneg, maxG_XBLUpos)/gforce_fac*gSizeGforce/DivBlue,                                           0, maxG_YBLUpos/gforce_fac*gSizeGforce/DivBlue, myImageGF_trac, myImageCircleS )
      if bRed:
        # draw full red overlay
        appDrawDotNSPil(1.0,0.20,0.20,0.5, wd, wd, max(maxG_XREDneg, maxG_XREDpos)/gforce_fac*gSizeGforce/DivRed, maxG_YREDneg/gforce_fac*gSizeGforce/DivRed,                                          0, myImageGF_trac, myImageCircleN )
        appDrawDotNSPil(1.0,0.20,0.20,0.5, wd, wd, max(maxG_XREDneg, maxG_XREDpos)/gforce_fac*gSizeGforce/DivRed,                                          0, maxG_YREDpos/gforce_fac*gSizeGforce/DivRed, myImageGF_trac, myImageCircleS )
      if bOrange:
        # draw full orange overlay
        appDrawDotNSPil(1.0,0.50,0.00,0.5, wd, wd, max(maxG_XORAneg, maxG_XORApos)/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange,                                             0, myImageGF_trac, myImageCircleN )
        appDrawDotNSPil(1.0,0.50,0.00,0.5, wd, wd, max(maxG_XORAneg, maxG_XORApos)/gforce_fac*gSizeGforce/DivOrange,                                             0, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, myImageGF_trac, myImageCircleS )
      if bYellow:
        # draw full yellow overlay
        appDrawDotNSPil(1.00,1.00,0.0,0.5, wd, wd, max(maxG_XYELneg, maxG_XYELpos)/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow,                                             0, myImageGF_trac, myImageCircleN )
        appDrawDotNSPil(1.00,1.00,0.0,0.5, wd, wd, max(maxG_XYELneg, maxG_XYELpos)/gforce_fac*gSizeGforce/DivYellow,                                             0, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, myImageGF_trac, myImageCircleS )
      if bGreen:
        # draw green overlay
        appDrawDotNSPil(0.0,1.00,0.00,0.5, wd, wd, max(maxG_XGREneg, maxG_XGREpos)/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen,                                            0, myImageGF_trac, myImageCircleN )
        appDrawDotNSPil(0.0,1.00,0.00,0.5, wd, wd, max(maxG_XGREneg, maxG_XGREpos)/gforce_fac*gSizeGforce/DivGreen,                                            0, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, myImageGF_trac, myImageCircleS )


      # newImg2.putalpha(mask)
      mask = myImageGF.split()[-1]
      myImageGF_trac.paste(myImageGF, (0,0), mask)
      #myImageGF_trac.paste(myImageGF, (0,0))


    ### image names always the same
    #localpostfix = time.strftime("%Y-%m-%d %H_%M") + postfix
    localpostfix = postfix
    myImageGF_trac.save('apps/python/GForce/result_gforce_trac'  + localpostfix + '.png')
    myImageGF.save(     'apps/python/GForce/result_gforce'       + localpostfix + '.png')

    ### image names with car + track
    #myImageGF.save( 'apps/python/GForce/result_g-f_' + carName + '_' + ac.getTrackName(0)+'.png')
  except:
    ac.log('G-Force error: ' + traceback.format_exc())








def appDrawLine5(r,g,b,a,x1,y1,x2,y2,y3):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  global bVertical
  if bVertical:
    ac.glVertex2f(x1,y1)
    ac.glVertex2f(x2,y1)
    ac.glVertex2f(x2,y2)
    ac.glVertex2f(x1,y3)
  else:
    ac.glVertex2f(x1,y1)
    ac.glVertex2f(x1,y3)
    ac.glVertex2f(x2,y2)
    ac.glVertex2f(x2,y1)
  ac.glEnd()

def appDrawLine5A(r,g,b,a,x1,y1,x2,y2,y3):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x1,y2)
  ac.glVertex2f(x2,y3)
  ac.glVertex2f(x2,y1)
  ac.glEnd()

def appDrawLine5B(r,g,b,a,x1,y1,x2,y2):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Triangles)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x2,y1)
  ac.glVertex2f(x2,y2)
  ac.glEnd()

# class GL:Lines,LineStrip,Triangles,Quads=range(4)

def appDrawLine6(r,g,b,a,h,x1,x2,y1,y2):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  # global bVertical
  if True:   ###bVertical:
    ac.glVertex2f(h-x1,y1)
    ac.glVertex2f(h-x2,y2)
    ac.glVertex2f(h+x2,y2)
    ac.glVertex2f(h+x1,y1)
  else:
    ac.glVertex2f(h-x1,y1)
    ac.glVertex2f(h-x2,y2)
    ac.glVertex2f(h+x2,y2)
    ac.glVertex2f(h+x1,y1)
  ac.glEnd()

def appDrawLine6B(r,g,b,a,h,x1,x2,y1,y2):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(h-x2,y2)
  ac.glVertex2f(h-x1,y1)
  ac.glVertex2f(h+x1,y1)
  ac.glVertex2f(h+x2,y2)
  ac.glEnd()

def appDrawLine7(r,g,b,a,h,x1,x2,y1,y2):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(h-x1,y1)
  ac.glVertex2f(h+x1,y1)
  ac.glVertex2f(h+x2,y2)
  ac.glVertex2f(h-x2,y2)
  ac.glEnd()

def appDrawLine666(r,g,b,a,h,x1,x2,y1,y2):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Triangles)
  ac.glVertex2f(h-x1,y2)
  ac.glVertex2f(h+x1,y2)
  ac.glVertex2f(h   ,y1)
  ac.glEnd()
  #ac.glQuad(x-(triangleWidth/2),104-(triangleWidth + triangleWidth/2),triangleWidth,triangleWidth/2)

def appDrawLine(x1,y1,x2,y2,width=4):
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1        ,y1)
  ac.glVertex2f(x2-width/2,y2)
  ac.glVertex2f(x2        ,y2)
  ac.glVertex2f(x1+width/2,y1)
  ac.glEnd()

def appDrawLine2(r,g,b,a,x1,y1,width=10,height=10):
  ac.glColor4f(r,g,b,a)
  ac.glQuad(x1,y1,width,height)

def appDrawLine3(r,g,b,a,x1,y1,x2,y2,height=4):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1-height/2,y1-height/2)
  ac.glVertex2f(x2,y2-height/2)
  ac.glVertex2f(x2,y2+height/2)
  ac.glVertex2f(x1-height/2,y1+height/2)
  ac.glEnd()

def appDrawLine3b(r,g,b,a,x1,y1,x2,y2,height=4):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x2,y2-3)
  ac.glVertex2f(x2,y2+3)
  ac.glVertex2f(x1,y1)
  ac.glEnd()

def appDrawLine3c(r,g,b,a,x1,y1,x2,y2,height=4):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x2,y1         )
  ac.glVertex2f(x1,y2-height)
  ac.glVertex2f(x1,y2+height)
  ac.glVertex2f(x2,y1)
  ac.glEnd()

def appDrawLine3d(r,g,b,a,x1,y1,x2,y2,height=4):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x2,y2)
  ac.glVertex2f(x2,y2)
  ac.glVertex2f(x1,y1)
  ac.glEnd()

def appDrawLine4(r,g,b,a,x1,y1,x2,y2): # simple non filled rectangle
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x1,y2)
  ac.glVertex2f(x2,y2)
  ac.glVertex2f(x2,y1)
  ac.glEnd()

def appDrawLine5(r,g,b,a,x1,y1,x2,y2,y3):
  ac.glColor4f(r,g,b,a)
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(x1,y1)
  ac.glVertex2f(x1,y3)
  ac.glVertex2f(x2,y2)
  ac.glVertex2f(x2,y1)
  ac.glEnd()

def appDrawLine6(r,g,b,a,h,x1,x2,y1,y2):
  global cspActive
  ac.glColor4f(r,g,b,a)
  #if cspActive:
  ac.glBegin(acsys.GL.Quads)
  ac.glVertex2f(h-x1,y1)
  ac.glVertex2f(h+x1,y1)
  ac.glVertex2f(h+x2,y2)
  ac.glVertex2f(h-x2,y2)
  ac.glEnd()
  #else:
  #    ac.glQuad(h-x1, h+x2, y2,)
      #ac.glQuad(x-(triangleWidth/2),104-(triangleWidth + triangleWidth/2),triangleWidth,triangleWidth/2)
      #ac.glQuad(0,y1,(x2-x1)*5,y2-y1)


def appDrawText(c, t, x, y, sz=12, align=ExtGL.FONT_ALIGN_CENTER):
  global f1, bCSPActive
  if bCSPActive:
    # ac.ext_glFontColor(f1.f, r, g, b, a)
    # ac.ext_glFontUse(f1.f, t, x, y, sz, align)
    ac.ext_glFontColor(f1.f, c, c, c, 1)
    ac.ext_glFontUse(f1.f, t, x, y, sz, align)

def appDrawTextRGB(r,g,b,a, t, x, y, sz=12, align=ExtGL.FONT_ALIGN_CENTER):
  global f1, bCSPActive
  if bCSPActive:
    # ac.ext_glFontColor(f1.f, r, g, b, a)
    # ac.ext_glFontUse(f1.f, t, x, y, sz, align)
    ac.ext_glFontColor(f1.f, r, g, b, a)
    ac.ext_glFontUse(f1.f, t, x, y, sz, align)


################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

def DrawBGgraphics():
  global box_w, box_w2, box_h, box_h2, offset, top, appWindow, texture_gforce, gSizeGforce, gColor, texture_gforce_1g, texture_gforce_2g, texture_gforce_3g, texture_gforce_4g
  global gforce_fac, max_gforce_fac, gOpacityG
  ac.glColor4f(1.0,1.0,1.0,gOpacityG/100)
  #wd = (box_w+12+gSizeGforce/2)/(gforce_fac)
  wd = gSizeGforce/gforce_fac
  if texid<=4: # texid>4 - dont draw any bg image
    ac.glQuadTextured(gSizeGforce-wd,
                    top+gSizeGforce-wd,wd*2,wd*2,
                    texture_gforce)
  if texid<=5: # texid>4 - dont draw any bg image
    # the bg-graphic with 1g
    ac.glQuadTextured(gSizeGforce-wd,
                    top+gSizeGforce-wd,wd*2,wd*2,
                    texture_gforce_1g)
    if gforce_fac>1.6:
      # the bg-graphic with 2g
      wd=wd*2   # *1.6666
      ac.glQuadTextured(gSizeGforce-wd,
                        top+gSizeGforce-wd,wd*2,wd*2,
                        texture_gforce_2g)
    if gforce_fac>2.6:
      # the bg-graphic with 3g
      wd=wd+wd/2   # *1.6666
      ac.glQuadTextured(gSizeGforce-wd,
                    top+gSizeGforce-wd,wd*2,wd*2,
                    texture_gforce_3g)
    if gforce_fac>3.6:
      # the bg-graphic with 4g
      wd=wd+wd/3   # *1.6666
      ac.glQuadTextured(gSizeGforce-wd,
                    top+gSizeGforce-wd,wd*2,wd*2,
                    texture_gforce_4g)

def DrawXYZForce(gforce_x, gforce_y, gforce_z, alpha):
  global box_w, box_w2, box_h, box_h2, offset, top, appWindow, texture_gforce, gSizeGforce, gColor, texture_dot2, texture_dot
  global gforce_fac, max_gforce_fac, DotSize
  wx = (gforce_x/gforce_fac)*gSizeGforce
  wy = (gforce_y/gforce_fac)*gSizeGforce
  wz = (gforce_z/gforce_fac)*gSizeGforce
  dS = gSizeGforce*2*DotSize/100

  ### the ball color
  if gforce_y<0.0:
    if gColor==0:
      ac.glColor4f(1, 1, 1, alpha)
    elif gColor==1:
      ac.glColor4f(1, 1-abs(gforce_y), 1-abs(gforce_y), alpha)
    else:
      ac.glColor4f(1, 1, 1-abs(gforce_y), alpha)
  else:
    if gColor==0:
      ac.glColor4f(1, 1, 1, alpha)
    elif gColor==1:
      ac.glColor4f(1-abs(gforce_y), 1, 1-abs(gforce_y), alpha)
    else:
      ac.glColor4f(1-abs(gforce_y), 1-abs(gforce_y), 1, alpha)

  #### the ball
  if alpha==1.0:
    # current gforce
    ac.glQuadTextured(gSizeGforce+wx-dS/2+1, top+gSizeGforce+wy-dS/2   , dS  , dS  , texture_dot2)
  else:
    # one of the history gforces, 2 pix smaller and 1 pix offset
    ac.glQuadTextured(gSizeGforce+wx-dS/2+2, top+gSizeGforce+wy-dS/2+1 , dS-2, dS-2, texture_dot)

  ### the vertical z force
  ### ignore z history when centered for (alpha=1) only
  if zForce and gforce_z and alpha==1.0:
    # color
    loc_gforce_z = abs(gforce_z)/2
    if gforce_z<0.0:
      if gColor==0:
        if alpha==1.0:
          ac.glColor4f(1,0.6,0.6,alpha)
        else:
          ac.glColor4f(0.8,0.4,0.4,alpha)
      elif gColor==1:
        ac.glColor4f(0.5+loc_gforce_z, 0.5-loc_gforce_z, 0.5-loc_gforce_z, alpha)
      else:
        ac.glColor4f(0.5+loc_gforce_z, 0.5+loc_gforce_z, 0.5-loc_gforce_z, alpha)
    else:
      if gColor==0:
        if alpha==1.0:
          ac.glColor4f(0.6,1,0.6,alpha)
        else:
          ac.glColor4f(0.4,0.8,0.4,alpha)
      elif gColor==1:
        ac.glColor4f(0.5-loc_gforce_z, 0.5+loc_gforce_z, 0.5-loc_gforce_z, alpha)
      else:
        ac.glColor4f(0.5-loc_gforce_z, 0.5-loc_gforce_z, 0.5+loc_gforce_z, alpha)

    if centeredZForce:
      # lines small
      ac.glQuad(        gSizeGforce-1      , top+gSizeGforce    ,  3, wz)
      ac.glQuad(        gSizeGforce-dS/2+1 , top+gSizeGforce+wz , dS,  3)
    else:
      # lines small
      ac.glQuad(        gSizeGforce+wx     -1, top+gSizeGforce+wy    ,  3, wz)
      ac.glQuad(        gSizeGforce+wx-dS/2+1, top+gSizeGforce+wy+wz , dS,  3)



def DrawXYZForceSM(gforce_x, gforce_y, alpha):
  global box_w, box_w2, box_h, box_h2, offset, top, appWindow, texture_gforce, gSizeGforce, gColor, texture_dot2, texture_dot
  global gforce_fac, max_gforce_fac, PNGmultGF, datagf, histDotSize, histDotSizePNG, bCSPActive
  wx = (gforce_x/gforce_fac)*gSizeGforce
  wy = (gforce_y/gforce_fac)*gSizeGforce
  rgb = (1,1,1)

  ### the ball/dot color
  if gforce_y<0.0:
    if gColor==0:
      ac.glColor4f(1-abs(gforce_y/4), 1-abs(gforce_y/4), 1-abs(gforce_y/4), alpha)
    elif gColor==1:
      ac.glColor4f(1,1-abs(gforce_y/2), 1-abs(gforce_y/2), alpha)
      #rgb =       (1,1-abs(gforce_y/2), 1-abs(gforce_y/2))
    else:
      ac.glColor4f(1,1, 1-abs(gforce_y/2), alpha)
      #rgb =       (1,1, 1-abs(gforce_y/2))
  else:
    if gColor==0:
      ac.glColor4f(1-abs(gforce_y/4), 1-abs(gforce_y/4), 1-abs(gforce_y/4), alpha)
    elif gColor==1:
      ac.glColor4f(1-abs(gforce_y/2), 1, 1-abs(gforce_y/2), alpha)
      #rgb =       (1-abs(gforce_y/2), 1, 1-abs(gforce_y/2))
    else:
      ac.glColor4f(1-abs(gforce_y/2), 1-abs(gforce_y/2), 1, alpha)
      #rgb =       (1-abs(gforce_y/2), 1-abs(gforce_y/2), 1)

  #### the point on mem texture
  ac.glQuadTextured(gSizeGforce+wx+1-histDotSize/2, top+gSizeGforce+wy-histDotSize/2, histDotSize, histDotSize, texture_dot2)




################################################################################################################################
################################################################################################################################
################################################################################################################################
################################################################################################################################
# paint g-force window

def onFormRender(deltaT):
  global l_gforce, l_tyre
  global gforce_x_act, gforce_y_act, gforce_z_act, gforce_last, gforce_max
  global act_idx, texture_gforce, texture_dot
  global gforce_fac, box_w, box_w2, box_h, box_h2, offset, top, appWindow, max_gforce_fac, base_gforce_fac
  global histCount, lastXYZ, currID, lastXY
  global bActiveTimer, fTimer, fTimer2, dataTimer, dataTimerUpdate, gOpacityBG, gOpacityFG, gOpacityTx, gColor, showGBars, smoothValue, showTraction, gOpacityHL
  global maxG_XGREpos, maxG_YGREpos, maxG_XREDpos, maxG_YREDpos, LimitYellow, LimitRed, LimitGreen, LimitOrange, maxG_XYELpos, maxG_YYELpos, maxG_XORApos, maxG_YORApos
  global maxG_XYELneg, maxG_YYELneg, maxG_XORAneg, maxG_YORAneg, maxG_XREDneg, maxG_YREDneg
  global maxG_XGREneg, maxG_YGREneg, maxG_XBLUpos, maxG_YBLUpos, maxG_XBLUneg, maxG_YBLUneg
  global texidNW, texidNE, texidSW, texidSE, texture_circle, texidN, texidS
  global lastCarFFB, boffset, bar_width, DoResetOnUSERFFBChange, currentCar, showArcade
  global ac_speed, ac_throttle, ac_brake, gforce_x, gforce_z, gforce_y, ac_ffb, ac_WSlip
  global ac_press, ac_temp, ac_dirt, ac_SR, ac_SA, ac_NdSlip, ac_Mz
  global bGreen, bYellow, bOrange, bRed, bBlue, CurrNumberOfTyresOut
  global DivGreen, DivYellow, DivOrange, DivRed, DivBlue, bScaleFixed
  global isInPits, bDoneResetInPits
  global b_gforceDec, userChanged
  global PNGmultGF, wmain, hmain, myImageGF, canvasGF
  global fadeoutime, timerIMG2, ghistT, histDotSize, gOpacityBGSub

  try:
    ### slowly updating ui stuff, also refresh labels
    fTimer2+=deltaT
    if fTimer2>0.1:
      fTimer2=0.0

      ### ffb
      if showFFB:
        if ac_ffb > gforce_max[6]:
          gforce_max[6] = ac_ffb
        # label
        if showGForce and not showTyres:
          ac.setText(l_gforce[6], "ffb\nmax: {:.2f}\ncurr: {:.3f}".format(gforce_max[6], ac_ffb))
        else:
          ac.setText(l_gforce[6], "ffb max: {:.2f}    curr: {:.3f}".format(gforce_max[6], ac_ffb))
        if gforce_max[6]>1.0:
          ac.setFontColor(l_gforce[6],1,0.5,0.5,gOpacityTx/100)
      else:
        ac.setText(l_gforce[6], "")


      # g-forces labels
      if showGForce:
        ac.setText(l_gforce[0], "{:.2f}g\nmin\n\n\n{:.1f}\n\n\nLon.\nmax\n{:.2f}g".format(gforce_max[2], gforce_y, abs(gforce_max[3])  ))
        ac.setText(l_gforce[3], "{:.1f}          Lat. max\n{:.2f}g".format( gforce_x, max( abs(gforce_max[0]), abs(gforce_max[1]) ) ))
        # ac.setText(l_gforce[0], "{:.1f}\n\n↑\n↓\n{:.2f}".format( gforce_y, max( abs(gforce_max[2]), abs(gforce_max[3]) ) ))
        # ac.setText(l_gforce[3], "{:.1f}     ←→ {:.2f}".format( gforce_x, max( abs(gforce_max[0]), abs(gforce_max[1]) ) ))
        # ac.setText(l_gforce[0], "{:.1f}\n⏶{:.2f}".format( gforce_y, max( abs(gforce_max[2]), abs(gforce_max[3]) ) ))
        # ac.setText(l_gforce[3], "{:.1f}\n⏶{:.2f}".format( gforce_x, max( abs(gforce_max[0]), abs(gforce_max[1]) ) ))

      if (showGBars or ac_speed<10) and zForce:
        ### standing still
        ac.setText(l_gforce[4], "\nVert. max\n{:.2f}g\n{:.1f}g".format(abs(gforce_max[4]), gforce_z))
      else:
        ac.setText(l_gforce[4], "")




    ### the bg-graphic or none
    DrawBGgraphics()

    #########################################################################################################
    ### g-force bar indicators, left and top
    if showGBars:
      wd = gSizeGforce
      ### small right/left indicators for gforce_x - on top
      loffset1 = min(gSizeGforce, abs(gforce_max[0])/gforce_fac)*gSizeGforce
      loffset2 = min(gSizeGforce, abs(gforce_max[1])/gforce_fac)*gSizeGforce
      drawBoxa(   wd-loffset1                  , 2, loffset1+loffset2, gSizeGforce/20-2, 0.5,0.5,0.5,0.5+gOpacityFG/100)
      loffset = abs(gforce_x/gforce_fac)*gSizeGforce
      if gforce_x<0.0:
        drawBoxa(wd-loffset                  , 1, loffset, gSizeGforce/20, 1,1,0.5, 0.5+gOpacityFG/50)
      else:
        drawBoxa(wd                          , 1, loffset, gSizeGforce/20, 1,1,0.5, 0.5+gOpacityFG/50)

      ### small up/down indicators for gforce_y - on left side
      loffset1 = min(gSizeGforce, abs(gforce_max[2])/gforce_fac) * gSizeGforce
      loffset2 = min(gSizeGforce, abs(gforce_max[3])/gforce_fac) * gSizeGforce
      drawBoxa(  2, wd-loffset1+1, gSizeGforce/20-2, loffset1+loffset2, 0.5,0.5,0.5,0.5+gOpacityFG/100)
      loffset = abs(gforce_y/gforce_fac*gSizeGforce)
      if gforce_y<0.0:
        drawBoxa(1, wd-loffset, gSizeGforce/20, loffset, 1,0.5,0.5, 0.5+gOpacityFG/50)
      else:
        drawBoxa(1, wd        , gSizeGforce/20, loffset, 0.5,1,0.5, 0.5+gOpacityFG/50)

    ##########################################################################################
    ### traction circles
    ### inspired by this https://www.youtube.com/watch?v=bYp2vvUgEqE
    if showTraction:
      dx=0
      dy=0
      # center
      # wd = (box_w+13+gSizeGforce/2)
      wd = gSizeGforce

      # draw full traction circles
      if gOpacityFG > 0:
        if bBlue:
          # draw full blue overlay
          appDrawDotNS(0.35,0.35,1.0,gOpacityFG/400, wd, wd, max(maxG_XBLUneg, maxG_XBLUpos)/gforce_fac, maxG_YBLUneg/gforce_fac,                       0, texidN, DivBlue )
          appDrawDotNS(0.35,0.35,1.0,gOpacityFG/400, wd, wd, max(maxG_XBLUneg, maxG_XBLUpos)/gforce_fac,                       0, maxG_YBLUpos/gforce_fac, texidS, DivBlue )
        if bRed:
        #  # draw full red overlay
          appDrawDotNS(1.0,0.20,0.20,gOpacityFG/400, wd, wd, max(maxG_XREDneg, maxG_XREDpos)/gforce_fac, maxG_YREDneg/gforce_fac,                       0, texidN, DivRed )
          appDrawDotNS(1.0,0.20,0.20,gOpacityFG/400, wd, wd, max(maxG_XREDneg, maxG_XREDpos)/gforce_fac,                       0, maxG_YREDpos/gforce_fac, texidS, DivRed )
        if bOrange:
          # draw full orange overlay
          #appDrawDotBothAxes(1.0,0.50,0.00,gOpacityFG/400, wd, wd, maxG_XORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_XORApos/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, texture_circle )
          appDrawDotNS(1.0,0.50,0.00,gOpacityFG/400, wd, wd, max(maxG_XORAneg, maxG_XORApos)/gforce_fac, maxG_YORAneg/gforce_fac,                       0, texidN, DivOrange )
          appDrawDotNS(1.0,0.50,0.00,gOpacityFG/400, wd, wd, max(maxG_XORAneg, maxG_XORApos)/gforce_fac,                       0, maxG_YORApos/gforce_fac, texidS, DivOrange )
        if bYellow:
          # draw full yellow overlay
          #appDrawDotBothAxes(1.00,1.00,0.0,gOpacityFG/400, wd, wd, maxG_XYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_XYELpos/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, texture_circle )
          appDrawDotNS(1.00,1.00,0.0,gOpacityFG/400, wd, wd, max(maxG_XYELneg, maxG_XYELpos)/gforce_fac, maxG_YYELneg/gforce_fac,                       0, texidN, DivYellow )
          appDrawDotNS(1.00,1.00,0.0,gOpacityFG/400, wd, wd, max(maxG_XYELneg, maxG_XYELpos)/gforce_fac,                       0, maxG_YYELpos/gforce_fac, texidS, DivYellow )
        if bGreen:
          # draw green overlay
          #appDrawDotBothAxes(0.0,1.00,0.00,gOpacityFG/400, wd, wd, maxG_XGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_XGREpos/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, texture_circle )
          appDrawDotNS(0.0,1.00,0.00,gOpacityFG/400, wd, wd, max(maxG_XGREneg, maxG_XGREpos)/gforce_fac, maxG_YGREneg/gforce_fac,                       0, texidN, DivGreen )
          appDrawDotNS(0.0,1.00,0.00,gOpacityFG/400, wd, wd, max(maxG_XGREneg, maxG_XGREpos)/gforce_fac,                       0, maxG_YGREpos/gforce_fac, texidS, DivGreen )

      ### draw traction circle highlights
      if gOpacityHL > 0:
        # draw part blue overlay
        if bBlue and abs(ac_SA[0])>LimitBlue or abs(ac_SA[1])>LimitBlue or abs(ac_SA[2])>LimitBlue or abs(ac_SA[3])>LimitBlue:
          currA = (abs(ac_SA[0])+abs(ac_SA[1])+abs(ac_SA[2])+abs(ac_SA[3]))*VisiMult/60  * gOpacityHL/100
          if showArcade:
            dx=min(gSizeGforce/4, currA * abs(gforce_x)/max_gforce_fac *gSizeGforce/4)
            dy=min(gSizeGforce/4, currA * abs(gforce_y)/max_gforce_fac *gSizeGforce/4)
          if gforce_x>0:
            if gforce_y>0:
              appDrawDot(0.5,0.5,1.0,min(10,currA),wd+dx, wd+dy, maxG_XBLUpos/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUneg/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUpos/gforce_fac*gSizeGforce/DivBlue, texidSE  )
            else:
              appDrawDot(0.5,0.5,1.0,min(10,currA),wd+dx, wd-dy, maxG_XBLUpos/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUneg/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUpos/gforce_fac*gSizeGforce/DivBlue, texidNE  )
          else:
            if gforce_y>0:
              appDrawDot(0.5,0.5,1.0,min(10,currA),wd-dx, wd+dy, maxG_XBLUpos/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUneg/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUpos/gforce_fac*gSizeGforce/DivBlue, texidSW  )
            else:
              appDrawDot(0.5,0.5,1.0,min(10,currA),wd-dx, wd-dy, maxG_XBLUpos/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUneg/gforce_fac*gSizeGforce/DivBlue, maxG_YBLUpos/gforce_fac*gSizeGforce/DivBlue, texidNW  )

        # draw part red overlay
        if bRed and abs(ac_NdSlip[0])>LimitRed or abs(ac_NdSlip[1])>LimitRed or abs(ac_NdSlip[2])>LimitRed or abs(ac_NdSlip[3])>LimitRed:
          currA = (abs(ac_NdSlip[0])+abs(ac_NdSlip[1])+abs(ac_NdSlip[2])+abs(ac_NdSlip[3]))*VisiMult /10  * gOpacityHL/100
          if showArcade:
            dx=min(gSizeGforce/4, currA * abs(gforce_x)/max_gforce_fac *gSizeGforce/4)
            dy=min(gSizeGforce/4, currA * abs(gforce_y)/max_gforce_fac *gSizeGforce/4)
          if gforce_x>0:
            if gforce_y>0:
              appDrawDot(1.0,0.25,0.25,min(10,currA),wd+dx, wd+dy, maxG_XREDpos/gforce_fac*gSizeGforce/DivRed, maxG_YREDneg/gforce_fac*gSizeGforce/DivRed, maxG_YREDpos/gforce_fac*gSizeGforce/DivRed, texidSE  )
            else:
              appDrawDot(1.0,0.25,0.25,min(10,currA),wd+dx, wd-dy, maxG_XREDpos/gforce_fac*gSizeGforce/DivRed, maxG_YREDneg/gforce_fac*gSizeGforce/DivRed, maxG_YREDpos/gforce_fac*gSizeGforce/DivRed, texidNE  )
          else:
            if gforce_y>0:
              appDrawDot(1.0,0.25,0.25,min(10,currA),wd-dx, wd+dy, maxG_XREDpos/gforce_fac*gSizeGforce/DivRed, maxG_YREDneg/gforce_fac*gSizeGforce/DivRed, maxG_YREDpos/gforce_fac*gSizeGforce/DivRed, texidSW  )
            else:
              appDrawDot(1.0,0.25,0.25,min(10,currA),wd-dx, wd-dy, maxG_XREDpos/gforce_fac*gSizeGforce/DivRed, maxG_YREDneg/gforce_fac*gSizeGforce/DivRed, maxG_YREDpos/gforce_fac*gSizeGforce/DivRed, texidNW  )

        # draw part orange overlay
        if bOrange and abs(ac_SR[0])>LimitOrange or abs(ac_SR[1])>LimitOrange or abs(ac_SR[2])>LimitOrange or abs(ac_SR[3])>LimitOrange:
          currA = (abs(ac_SR[0])+abs(ac_SR[1])+abs(ac_SR[2])+abs(ac_SR[3]))*VisiMult*2  * gOpacityHL/100
          if showArcade:
            dx=min(gSizeGforce/4, currA * abs(gforce_x)/max_gforce_fac *gSizeGforce/4)
            dy=min(gSizeGforce/4, currA * abs(gforce_y)/max_gforce_fac *gSizeGforce/4)
          if gforce_x>0:
            if gforce_y>0:
              appDrawDot(1.0,0.5,0.0,min(10,currA),wd+dx, wd+dy, maxG_XORApos/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, texidSE )
            else:
              appDrawDot(1.0,0.5,0.0,min(10,currA),wd+dx, wd-dy, maxG_XORApos/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, texidNE )
          else:
            if gforce_y>0:
              appDrawDot(1.0,0.5,0.0,min(10,currA),wd-dx, wd+dy, maxG_XORApos/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, texidSW )
            else:
              appDrawDot(1.0,0.5,0.0,min(10,currA),wd-dx, wd-dy, maxG_XORApos/gforce_fac*gSizeGforce/DivOrange, maxG_YORAneg/gforce_fac*gSizeGforce/DivOrange, maxG_YORApos/gforce_fac*gSizeGforce/DivOrange, texidNW )

        # draw part yellow overlay
        if bYellow and abs(ac_Mz[0])>LimitYellow or abs(ac_Mz[1])>LimitYellow or abs(ac_Mz[2])>LimitYellow or abs(ac_Mz[3])>LimitYellow:
          currA = (abs(ac_Mz[0])+abs(ac_Mz[1])+abs(ac_Mz[2])+abs(ac_Mz[3]))/500*VisiMult  * gOpacityHL/100
          if showArcade:
            dx=min(gSizeGforce/4, currA * abs(gforce_x)/max_gforce_fac *gSizeGforce/4)
            dy=min(gSizeGforce/4, currA * abs(gforce_y)/max_gforce_fac *gSizeGforce/4)
          if gforce_x>0:
            if gforce_y>0:
              appDrawDot(1.0,1.0,0.0,min(10,currA),wd+dx, wd+dy, maxG_XYELpos/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, texidSE )
            else:
              appDrawDot(1.0,1.0,0.0,min(10,currA),wd+dx, wd-dy, maxG_XYELpos/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, texidNE )
          else:
            if gforce_y>0:
              appDrawDot(1.0,1.0,0.0,min(10,currA),wd-dx, wd+dy, maxG_XYELpos/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, texidSW )
            else:
              appDrawDot(1.0,1.0,0.0,min(10,currA),wd-dx, wd-dy, maxG_XYELpos/gforce_fac*gSizeGforce/DivYellow, maxG_YYELneg/gforce_fac*gSizeGforce/DivYellow, maxG_YYELpos/gforce_fac*gSizeGforce/DivYellow, texidNW )

        # draw part green overlay
        if bGreen and type(ac_WSlip)!=int:
          if abs(ac_WSlip[0])>LimitGreen or abs(ac_WSlip[1])>LimitGreen or abs(ac_WSlip[2])>LimitGreen or abs(ac_WSlip[3])>LimitGreen:
            currA = (abs(ac_WSlip[0])+abs(ac_WSlip[1])+abs(ac_WSlip[2])+abs(ac_WSlip[3]))*VisiMult /10  * gOpacityHL/100
            if showArcade:
              dx=min(gSizeGforce/4, currA * abs(gforce_x)/max_gforce_fac *gSizeGforce/4)
              dy=min(gSizeGforce/4, currA * abs(gforce_y)/max_gforce_fac *gSizeGforce/4)
            if gforce_x>0:
              if gforce_y>0:
                appDrawDot(0.0,1.0,0.0,min(10,currA),wd+dx, wd+dy, maxG_XGREpos/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, texidSE )
              else:
                appDrawDot(0.0,1.0,0.0,min(10,currA),wd+dx, wd-dy, maxG_XGREpos/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, texidNE )
            else:
              if gforce_y>0:
                appDrawDot(0.0,1.0,0.0,min(10,currA),wd-dx, wd+dy, maxG_XGREpos/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, texidSW )
              else:
                appDrawDot(0.0,1.0,0.0,min(10,currA),wd-dx, wd-dy, maxG_XGREpos/gforce_fac*gSizeGforce/DivGreen, maxG_YGREneg/gforce_fac*gSizeGforce/DivGreen, maxG_YGREpos/gforce_fac*gSizeGforce/DivGreen, texidNW )






    ### tyres
    if showTyres:
      cval = [0.0,0.0,0.0,0.0]
      for idx in range(4):
        cval[idx]=abs((70-ac_temp[idx])/70)*1  # -0.5...0.5
        if info.physics.tyreWear[idx] < 100.0:
          appSetFontColorTyres(l_tyre[idx], cval[idx], ac_temp[idx])
          if PressID:
            if TempID:
              ac.setText(l_tyre[idx], "{:.1f}psi\n{:.1f}°F\n{:.2f}%".format(ac_press[idx],         ac_temp[idx] * 9/5 + 32, 100-info.physics.tyreWear[idx]))
            else:
              ac.setText(l_tyre[idx], "{:.1f}psi\n{:.1f}°C\n{:.2f}%".format(ac_press[idx],         ac_temp[idx]           , 100-info.physics.tyreWear[idx]))
          else:
            if TempID:
              ac.setText(l_tyre[idx], "{:.2f}bar\n{:.1f}°F\n{:.2f}%".format(ac_press[idx]/14.5038, ac_temp[idx] * 9/5 + 32, 100-info.physics.tyreWear[idx]))
            else:
              ac.setText(l_tyre[idx], "{:.2f}bar\n{:.1f}°C\n{:.2f}%".format(ac_press[idx]/14.5038, ac_temp[idx]           , 100-info.physics.tyreWear[idx]))
        else:
          appSetFontColorTyres(l_tyre[idx], cval[idx], ac_temp[idx])
          if PressID:
            if TempID:
              ac.setText(l_tyre[idx], "{:.1f}psi\n{:.1f}°F\n{:.1f}%".format(ac_press[idx]        , ac_temp[idx] * 9/5 + 32, 100-info.physics.tyreWear[idx]))
            else:
              ac.setText(l_tyre[idx], "{:.1f}psi\n{:.1f}°C\n{:.1f}%".format(ac_press[idx]        , ac_temp[idx]           , 100-info.physics.tyreWear[idx]))
          else:
            if TempID:
              ac.setText(l_tyre[idx], "{:.2f}bar\n{:.1f}°F\n{:.1f}%".format(ac_press[idx]/14.5038, ac_temp[idx] * 9/5 + 32, 100-info.physics.tyreWear[idx]))
            else:
              ac.setText(l_tyre[idx], "{:.2f}bar\n{:.1f}°C\n{:.1f}%".format(ac_press[idx]/14.5038, ac_temp[idx]           , 100-info.physics.tyreWear[idx]))

      y_front = top+5
      y_rear  = y_front+box_h2+15
      x_left  = offset+gSizeGforce*0.5
      x_right = offset+gSizeGforce*0.5+35
      drawBox(x_left  - (x_left  % 2),  y_front, 15, box_h2, 1.0, (5.0-ac_dirt[0])/5.0, 0.0 if ac_dirt[0] > 1.0 else 1.0-ac_dirt[0])
      drawBox(x_right - (x_right % 2),  y_front, 15, box_h2, 1.0, (5.0-ac_dirt[1])/5.0, 0.0 if ac_dirt[1] > 1.0 else 1.0-ac_dirt[1])
      drawBox(x_left  - (x_left  % 2),  y_rear , 15, box_h2, 1.0, (5.0-ac_dirt[2])/5.0, 0.0 if ac_dirt[2] > 1.0 else 1.0-ac_dirt[2])
      drawBox(x_right - (x_right % 2),  y_rear , 15, box_h2, 1.0, (5.0-ac_dirt[3])/5.0, 0.0 if ac_dirt[3] > 1.0 else 1.0-ac_dirt[3])

      appDrawTyreBar(cval[0], ac_temp[0], x_left+2 , y_front+1, 10, box_h2-2)
      appDrawTyreBar(cval[1], ac_temp[1], x_right+2, y_front+1, 10, box_h2-2)
      appDrawTyreBar(cval[2], ac_temp[2], x_left+2 , y_rear +1, 10, box_h2-2)
      appDrawTyreBar(cval[3], ac_temp[3], x_right+2, y_rear +1, 10, box_h2-2)

      if ac_speed > 1.0:
        tySlipFact=0.5
        ac.glColor4f(1.0, 1.0-abs(ac_SA[0]), 0.0, abs(ac_SA[0]*tySlipFact))
        #ac.glQuad(x_left+2, y_front+1, 10, box_h2-2)
        if abs(ac_SA[0])>0.05:
          ac.glQuad(x_left+4+11,  y_front+1, 6, min(box_h2, abs(ac_SA[0]*tySlipFact)) )

        ac.glColor4f(1.0, 1.0-abs(ac_SA[1]), 0.0, abs(ac_SA[1]*tySlipFact))
        #ac.glQuad(x_right+2, y_front+1, 10, box_h2-2)
        if abs(ac_SA[1])>0.05:
          ac.glQuad(x_right+3-12, y_front+1, 6, min(box_h2, abs(ac_SA[1]*tySlipFact)) )

        ac.glColor4f(1.0, 1.0-abs(ac_SA[2]), 0.0, abs(ac_SA[2]*tySlipFact))
        #ac.glQuad(x_left+2, y_rear +1, 10, box_h2-2)
        if abs(ac_SA[2])>0.05:
          ac.glQuad(x_left+4+11,  y_rear+1,  6, min(box_h2, abs(ac_SA[2]*tySlipFact)) )

        ac.glColor4f(1.0, 1.0-abs(ac_SA[3]), 0.0, abs(ac_SA[3]*tySlipFact))
        #ac.glQuad(x_right+2, y_rear +1, 10, box_h2-2)
        if abs(ac_SA[3])>0.05:
          ac.glQuad(x_right+3-12, y_rear+1,  6, min(box_h2, abs(ac_SA[3]*tySlipFact)) )

    ### pedals: throttle/gas, brake and/or FFB
    if showPedals:
      # based on appwindow size: offset+2*box_w+55, top+2*box_h+12+gSizeGforce)
      drawBox(offset, top+2*box_h+gSizeGforce+boffset   , bar_width, 10, 1.0, 1.0, 1.0)
      drawBox(offset, top+2*box_h+gSizeGforce+boffset+15, bar_width, 10, 1.0, 1.0, 1.0)
      if showFFB:
        drawBox(offset, top+2*box_h+gSizeGforce+boffset+30, bar_width, 10, 1.0, 1.0, 1.0)

      ac.glColor3f(0.0,0.8,0.0)
      ac.glQuad(offset+2, top+2*box_h+gSizeGforce+boffset+1, ac_throttle*(bar_width-4), 7)
      ac.glColor3f(0.8,0.0,0.0)
      ac.glQuad(offset+2, top+2*box_h+gSizeGforce+boffset+16, ac_brake*(bar_width-4), 7)
      if showFFB:
        if ac_ffb>1:
          ac.glColor3f(0.5+ac_ffb/2,0.75,0.5+ac_ffb)
        else:
          ac.glColor3f(0.75,0.75,ac_ffb/2)
        ac.glQuad(offset+2, top+2*box_h+gSizeGforce+boffset+31, ac_ffb/2*(bar_width-4), 7)

    timerIMG2 += deltaT

    ### draw all gforces in history array
    if showGForce:
      if bCSPActive:
        if timerIMG2>fadeoutime:
          timerIMG2 = 0.0
          ### starts drawing into render target, not on screen
          ac.ext_bindRenderTarget(rtIndexGF)
          # paint over myself with a black almost transparent image
          ac.glColor4f(0,0,0,0.1) # just barely visible overall, but darkens image enough
          ac.glBegin(acsys.GL.Quads)
          # mode: 0 for opaque, 1 for alpha blend, 2 for alpha test, 4 for additive, 5 for multiplicative
          ac.ext_glSetBlendMode(1)
          ac.ext_glSetTexture(rtIndex0, 0)
          ac.ext_glVertexTex((0,0,0,0))
          ac.ext_glVertexTex((0,wmain*2,0,1))
          ac.ext_glVertexTex((wmain*2,wmain*2,1,1))
          ac.ext_glVertexTex((wmain*2,0,1,0))
          #ac.ext_glSetBlendMode(0)
          ac.glEnd()
          ### restores original render target
          ac.ext_restoreRenderTarget()

        ### blend painted image on app window
        ac.glColor4f(1,1,1,ghistT/100.0)
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glSetTexture(rtIndexGF, 0)
        ac.ext_glVertexTex((0,0,0,0))
        ac.ext_glVertexTex((0,wmain,0,1))
        ac.ext_glVertexTex((wmain,wmain,1,1))
        ac.ext_glVertexTex((wmain,0,1,0))
        ac.glEnd()
      else:
        DrawXYZForceSM(gforce_x, gforce_y, 1)

      ### draw all gforces in history array on app window
      if histCount!=0: # with trail
        lastXYZ[currID][0] = gforce_x
        lastXYZ[currID][1] = gforce_y
        lastXYZ[currID][2] = gforce_z
        localID = currID + 1
        if localID >= histCount: # wrap around the history array
          localID = 0
        count = 0
        while count < histCount:
          if lastXYZ[localID][0] != 111.0:
            if histVisi>0:
              DrawXYZForce(lastXYZ[localID][0], lastXYZ[localID][1], lastXYZ[localID][2], count/histCount/histVisi*2)
            else:
              DrawXYZForce(lastXYZ[localID][0], lastXYZ[localID][1], lastXYZ[localID][2], 0.99)
          count += 1
          localID += 1
          if localID >= histCount: # wrap around the history array
            localID = 0
        DrawXYZForce(lastXYZ[currID][0], lastXYZ[currID][1], lastXYZ[currID][2], 1)
        currID += 1
        if currID >= histCount:
          currID = 0
      else: # without trail
        DrawXYZForce(gforce_x, gforce_y, gforce_z, 1)
  except:
    ac.log('G-Force error: ' + traceback.format_exc())













################################################################################################################################
################################################################################################################################
################################################################################################################################
################################################################################################################################
### data gathering + result image painting

def acUpdate(deltaT):
  global gforce_x_act, gforce_y_act, gforce_z_act, gforce_last, gforce_max
  global act_idx, act_idx2, texture_gforce, texture_dot
  global gforce_fac, box_w, box_w2, box_h, box_h2, offset, top, appWindow, max_gforce_fac, base_gforce_fac
  global histCount, lastXYZ, currID, lastXY
  global bActiveTimer, fTimer, fTimer2, dataTimer, dataTimerUpdate, gOpacityBG, gOpacityFG, gOpacityTx, gColor, showGBars, smoothValue, showTraction, gOpacityHL
  global maxG_XGREpos, maxG_YGREpos, maxG_XREDpos, maxG_YREDpos, LimitYellow, LimitRed, LimitGreen, LimitOrange, maxG_XYELpos, maxG_YYELpos, maxG_XORApos, maxG_YORApos
  global maxG_XYELneg, maxG_YYELneg, maxG_XORAneg, maxG_YORAneg, maxG_XREDneg, maxG_YREDneg
  global maxG_XGREneg, maxG_YGREneg, maxG_XBLUpos, maxG_YBLUpos, maxG_XBLUneg, maxG_YBLUneg
  global texidNW, texidNE, texidSW, texidSE, texture_circle
  global lastCarFFB, boffset, bar_width, DoResetOnUSERFFBChange, currentCar, showArcade
  global ac_speed, ac_throttle, ac_brake, gforce_x, gforce_z, gforce_y, ac_ffb, ac_WSlip
  global ac_press, ac_temp, ac_dirt, ac_SR, ac_SA, ac_NdSlip, ac_Mz
  global bGreen, bYellow, bOrange, bRed, bBlue, CurrNumberOfTyresOut
  global DivGreen, DivYellow, DivOrange, DivRed, DivBlue, bScaleFixed
  global isInPits, bDoneResetInPits, b_gforceDec, userChanged
  global PNGmultGF, wmain, hmain, canvasGF, myImageGF
  global fadeoutime, timerIMG2, ghistT, histDotSize
  global fontSize, valx, valy, valxx, valyy, SlipAng_Front, SlipAng_Rear
  global datagf, SteeringAngle, bCSPActive, rtIndexGF
  global ac_wspeed, revRange, Gears, geardatacount, geardatacountdone


  ### hide buttons when timer runs out
  if bActiveTimer:
    fTimer -= deltaT
    if fTimer <= 0.0:
      bActiveTimer = False
      appHideButtons()

  try:

    ### lazy data update for smoother graph
    dataTimer += deltaT
    if dataTimer > dataTimerUpdate:
      dataTimer=0.0

      # ac.log('GForce app: bCSPActive=' +str(bCSPActive))
      if bCSPActive and rtIndexGF>-1:
        ac.ext_generateMips(rtIndexGF)

      ac.setBackgroundOpacity(appWindow, float(gOpacityBG/100.0) )

      CurrNumberOfTyresOut         = info.physics.numberOfTyresOut
      currentCar                   = ac.getFocusedCar()
      ac_speed                     = ac.getCarState(currentCar, acsys.CS.SpeedKMH)
      SteeringAngle                = ac.getCarState(currentCar, acsys.CS.Steer)

      gforce_x, gforce_z, gforce_y = ac.getCarState(currentCar, acsys.CS.AccG)
      ac_throttle                  = ac.getCarState(currentCar, acsys.CS.Gas)
      ac_brake                     = ac.getCarState(currentCar, acsys.CS.Brake)
      ac_press                     = ac.getCarState(currentCar, acsys.CS.DynamicPressure)
      ac_temp                      = ac.getCarState(currentCar, acsys.CS.CurrentTyresCoreTemp)
      ac_dirt                      = ac.getCarState(currentCar, acsys.CS.TyreDirtyLevel)
      ac_ffb                       = ac.getCarState(currentCar, acsys.CS.LastFF)
      currentRPM                   = ac.getCarState(currentCar, acsys.CS.RPM)
      currentGear                  = ac.getCarState(currentCar, acsys.CS.Gear)

      ac_SR                        = ac.getCarState(currentCar, acsys.CS.SlipRatio)
      ac_SA                        = ac.getCarState(currentCar, acsys.CS.SlipAngle)
      ac_NdSlip                    = ac.getCarState(currentCar, acsys.CS.NdSlip)
      # wth its all 0 the official way? only working with help from SharedMem
      #ac_WSlip                    = ac.getCarState(currentCar, acsys.CS.TyreSlip)
      ac_WSlip                     = info.physics.wheelSlip
      ac_Mz                        = ac.getCarState(currentCar, acsys.CS.Mz)

      ac_wspeed                    = ac.getCarState(currentCar, acsys.CS.WheelAngularSpeed)

      SlipAng_Front = (ac_SA[0] + ac_SA[1]) / gSteeringNormalizer * gSizeGforce
      SlipAng_Rear  = (ac_SA[2] + ac_SA[3]) / gSteeringNormalizer * gSizeGforce

      ### set maximas for arcade traction circles
      ### ignore high z, and abnormal x/y above user setting
      ### set sensitive max values only in normal situations
      ### limit max values, only in normal driving situations
      if (  ac_speed>10
        and abs(gforce_z)<1.0
        #and abs(gforce_x)<max_gforce_fac*10 \
        #and abs(gforce_y)<max_gforce_fac*1.5 \
        and CurrNumberOfTyresOut < 4
        and ac_SR[0]<2.0 and ac_SR[1]<2.0 and ac_SR[2]<2.0 and ac_SR[3]<2.0
        and ac_NdSlip[0]<2.0 and ac_NdSlip[1]<2.0 and ac_NdSlip[2]<2.0 and ac_NdSlip[3]<2.0) :
        #and abs(gforce_x)<max(abs(gforce_max[0])*1.5,abs(gforce_max[1])*1.5) and abs(gforce_y)<max(abs(gforce_max[2])*1.5,abs(gforce_max[3])*1.5):

        if gforce_x < gforce_max[0]:
          gforce_max[0] = gforce_x
        if gforce_x > gforce_max[1]:
          gforce_max[1] = gforce_x

        if gforce_y < gforce_max[2]:
          gforce_max[2] = gforce_y
        if gforce_y > gforce_max[3]:
          gforce_max[3] = gforce_y

        # if bScaleFixed:
        #   ### limit gforce to user setting
        #newgforce_fac = min(base_gforce_fac, max(max_gforce_fac, gforce_fac, abs(math.ceil(gforce_max[0])), abs(math.floor(gforce_max[1])), abs(math.ceil(gforce_max[2])), abs(math.floor(gforce_max[3]) )))
        # else:
        #newgforce_fac = max(base_gforce_fac, max( (abs(gforce_max[0])), (abs(gforce_max[1])), (abs(gforce_max[2])), (abs(gforce_max[3])) ) )

        ### limit gforce to user setting
        #newgforce_fac = min(base_gforce_fac, max(max_gforce_fac, gforce_fac, abs(math.ceil(gforce_max[0])), abs(math.floor(gforce_max[1])), abs(math.ceil(gforce_max[2])), abs(math.floor(gforce_max[3]) )))

        ### limit gforce to currentmax
        if not userChanged:
          newgforce_fac = math.ceil(max( math.ceil(abs(gforce_max[0])), math.ceil(abs(gforce_max[1])), math.ceil(abs(gforce_max[2])), math.ceil(abs(gforce_max[3])) ))
          if newgforce_fac - gforce_fac > 0.1:
            gforce_fac = newgforce_fac
            base_gforce_fac = gforce_fac
            max_gforce_fac = gforce_fac
            ac.setText(b_gforceDec     , '- ' + str(round(base_gforce_fac,1)) + '\n     MAX g')

        if gforce_z < gforce_max[4]:
          gforce_max[4] = gforce_z
        if gforce_z > gforce_max[5]:
          gforce_max[5] = gforce_z

        if showTraction or b_arcade:
          if (abs(ac_WSlip[0])<LimitGreen*2 and abs(ac_WSlip[1])<LimitGreen*2) or (abs(ac_WSlip[2])<LimitGreen*2 and abs(ac_WSlip[3])<LimitGreen*2):
            # set max green tyreslip
            if gforce_y<0:
              maxG_YGREneg = min(max( maxG_YGREneg  , abs(gforce_y)), max_gforce_fac)
            else:
              maxG_YGREpos = min(max( maxG_YGREpos  , abs(gforce_y)), max_gforce_fac)
            if gforce_x<0:
              maxG_XGREneg = min(max( maxG_XGREneg  , abs(gforce_x)), max_gforce_fac)
            else:
              maxG_XGREpos = min(max( maxG_XGREpos  , abs(gforce_x)), max_gforce_fac)
          if (abs(ac_Mz[0])<LimitYellow and abs(ac_Mz[1])<LimitYellow) or (abs(ac_Mz[2])<LimitYellow and abs(ac_Mz[3])<LimitYellow):
            # set max yellow Mz
            if gforce_y<0:
              maxG_YYELneg = min(max( maxG_YYELneg  , abs(gforce_y)), max_gforce_fac)
            else:
              maxG_YYELpos = min(max( maxG_YYELpos  , abs(gforce_y)), max_gforce_fac)
            if gforce_x<0:
              maxG_XYELneg = min(max( maxG_XYELneg  , abs(gforce_x)), max_gforce_fac)
            else:
              maxG_XYELpos = min(max( maxG_XYELpos  , abs(gforce_x)), max_gforce_fac)
          if (abs(ac_SR[0])<LimitOrange and abs(ac_SR[1])<LimitOrange) or (abs(ac_SR[2])<LimitOrange and abs(ac_SR[3])<LimitOrange):
            # set max orange SlipRatio
            if gforce_y<0:
              maxG_YORAneg = min(max( maxG_YORAneg  , abs(gforce_y)), max_gforce_fac)
            else:
              maxG_YORApos = min(max( maxG_YORApos  , abs(gforce_y)), max_gforce_fac)
            if gforce_x<0:
              maxG_XORAneg = min(max( maxG_XORAneg  , abs(gforce_x)), max_gforce_fac)
            else:
              maxG_XORApos = min(max( maxG_XORApos  , abs(gforce_x)), max_gforce_fac)
          if (abs(ac_NdSlip[0])<LimitRed and abs(ac_NdSlip[1])<LimitRed) or (abs(ac_NdSlip[2])<LimitRed and abs(ac_NdSlip[3])<LimitRed):
            # set max red NdSlip
            if gforce_y<0:
              maxG_YREDneg = min(max( maxG_YREDneg  , abs(gforce_y)), max_gforce_fac)
            else:
              maxG_YREDpos = min(max( maxG_YREDpos  , abs(gforce_y)), max_gforce_fac)
            if gforce_x<0:
              maxG_XREDneg = min(max( maxG_XREDneg  , abs(gforce_x)), max_gforce_fac)
            else:
              maxG_XREDpos = min(max( maxG_XREDpos  , abs(gforce_x)), max_gforce_fac)
          if (abs(ac_SA[0])<LimitBlue and abs(ac_SA[1])<LimitBlue) or (abs(ac_SA[2])<LimitBlue and abs(ac_SA[3])<LimitBlue):
            # set max blue SlipAngle
            if gforce_y<0:
              maxG_YBLUneg = min(max( maxG_YBLUneg  , abs(gforce_y)), max_gforce_fac)
            else:
              maxG_YBLUpos = min(max( maxG_YBLUpos  , abs(gforce_y)), max_gforce_fac)
            if gforce_x<0:
              maxG_XBLUneg = min(max( maxG_XBLUneg  , abs(gforce_x)), max_gforce_fac)
            else:
              maxG_XBLUpos = min(max( maxG_XBLUpos  , abs(gforce_x)), max_gforce_fac)


      # count down overshooting gforces
      if bScaleFixed:
        if gforce_max[0]<-gforce_fac:
          if gforce_max[0]+0.05 > -gforce_fac:
            gforce_max[0] = -gforce_fac
          else:
            gforce_max[0] = gforce_max[0]+0.05
        if gforce_max[1]> gforce_fac:
          if gforce_max[1]-0.05 < gforce_fac:
            gforce_max[1] = gforce_fac
          else:
            gforce_max[1] = gforce_max[1]-0.05
        if gforce_max[2]<-gforce_fac:
          if gforce_max[2]+0.05 > -gforce_fac:
            gforce_max[2] = -gforce_fac
          else:
            gforce_max[2] = gforce_max[2]+0.05
        if gforce_max[3]> gforce_fac:
          if gforce_max[3]-0.05 < gforce_fac:
            gforce_max[3] = gforce_fac
          else:
            gforce_max[3] = gforce_max[3]-0.05
        if gforce_max[4]<-gforce_fac:
          gforce_max[4] = gforce_max[4]+0.05
        if gforce_max[5]> gforce_fac:
          gforce_max[5] = gforce_max[5]-0.05

      ### FFB max reset on user FFB mult change
      if DoResetOnUSERFFBChange:
        currCarFFB = ac.getCarFFB()
        if lastCarFFB != currCarFFB:
          lastCarFFB = currCarFFB
          onReset()
          ac.setFontColor(l_gforce[6],1,1,1,gOpacityTx/100)

      global g_Reset_When_In_Pits
      if g_Reset_When_In_Pits:
        if not isInPits and (ac.isCarInPitlane(currentCar) or ac.isCarInPit(currentCar)):
          isInPits = True
          bDoneResetInPits = True
          # if saveResults:
          #   ### not a good idea, double saved when user quits after pits
          #   runSaveImagesThread('_pit')
          onReset()

        if isInPits and not (ac.isCarInPitlane(currentCar) or ac.isCarInPit(currentCar)):
          isInPits = False
          bDoneResetInPits = False


      # paint on pil image lat vs vert gforce
      global wx2, wy2, wz2
      wx2 = (gforce_x/gforce_fac)*gSizeGforce
      wy2 = (gforce_y/gforce_fac)*gSizeGforce
      wz2 = (gforce_z/gforce_fac)*gSizeGforce
      datagf+=1
      if gforce_y<0.0:
        if gColor==0:
          rgb =       (1-abs(gforce_y/4), 1-abs(gforce_y/4), 1-abs(gforce_y/4))
        elif gColor==1:
          rgb =       (1,1-abs(gforce_y/2), 1-abs(gforce_y/2))
        else:
          rgb =       (1,1, 1-abs(gforce_y/2))
      else:
        if gColor==0:
          rgb =       (1-abs(gforce_y/4), 1-abs(gforce_y/4), 1-abs(gforce_y/4))
        elif gColor==1:
          rgb =       (1-abs(gforce_y/2), 1, 1-abs(gforce_y/2))
        else:
          rgb =       (1-abs(gforce_y/2), 1-abs(gforce_y/2), 1)
      canvasGF.rectangle((PNGmultGF*(gSizeGforce+wx2+1)-histDotSizePNG/2, PNGmultGF*(top+gSizeGforce+wy2)-histDotSizePNG/2,
                          PNGmultGF*(gSizeGforce+wx2+1)+histDotSizePNG/2, PNGmultGF*(top+gSizeGforce+wy2)+histDotSizePNG/2),
                          # fill=(min(255, int(rgb[0]*100)), min(255, int(rgb[1]*100)), min(255, int(rgb[2]*100)) ) )
                          fill=(int(rgb[0]*255),int(rgb[1]*255), int(rgb[2]*255)) )
      if bCSPActive and rtIndexGF>0:
        ### start drawing into render target, not on screen
        ac.ext_bindRenderTarget(rtIndexGF)

        ## paint on memory texture
        DrawXYZForceSM(gforce_x, gforce_y, 1)

        ### restores original render target to continue drawing app to
        ac.ext_restoreRenderTarget()
  except:
    ac.log('G-Force error: ' + traceback.format_exc())

