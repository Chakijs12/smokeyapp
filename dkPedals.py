######################################################################################
# dkPedals.py
# Dennis Karlsson (dennis@dennis.se)
#
# 2018-06-14	v0.1	First version
# 2018-08-31	v0.2	Added FFBClip frame
# 2018-09-01	v0.3	Made it possible to hide pedals
# 2018-09-04	v0.4	Hide clutch if not used. Hide FFB if not exist. (demo replay)
#						Better handling of config file. Bugfixes
# 2019-01-05	v0.5	Fixed so it shows pedals for the focused car.
#						Added text labels to boost and FFB bar.
# 2019-02-27	v0.6	Added support for handbrake via AC patch v0.1.25-preview51 or later.
#						https://acstuff.ru/patch/ needs to be installed for this to work.
#						Bugfixes.
# 2019-04-10	v0.7	Don't show handbrake if not used.
# 2019-10-03	v0.8	Fixed bug in _defaults.ini file.
#						Added ingame configuration. All dkApps needs to be updated for this to work.
#						FFB bar does not autohide anymore, it was very irritating. 
#						Added steering input visualization (with blinking if not centered).
#						dkConfigHandler is updated.
# 2020-02-07	v0.9	Labels was not cleared when disabled. Fixed.
# 2020-05-08	v1.0	Set maximum ffb to show.
# 2020-08-30	v1.1	Added option to show turbo pressure as psi.
# 2021-04-05	v1.2	Added text labels to pedals.
# 2022-05-02	v1.3	Added red bar on 100% FFB
#
######################################################################################

import ac, acsys, dkCH, time
app = "dkPedals"
ac.log("["+app+"] Starting...")

def strToBool(s):
	if s == 'True':
		return True
	elif s == 'False':
		return False
	else:
		ac.log("["+app+"] StrToBool error.")

# Handle config
dkCH.init(app)
dkPedalsSettingsClutch				= strToBool(dkCH.rc(app, app, 'clutch', 'True'))					# ingame conf
dkPedalsSettingsBrake				= strToBool(dkCH.rc(app, app, 'brake', 'True'))						# ingame conf
dkPedalsSettingsThrottle			= strToBool(dkCH.rc(app, app, 'throttle', 'True'))					# ingame conf
dkPedalsSettingsHandbrake			= strToBool(dkCH.rc(app, app, 'handbrake', 'True'))					# ingame conf
dkPedalsSettingsTurbo				= strToBool(dkCH.rc(app, app, 'turbo', 'True'))						# ingame conf
dkPedalsSettingsFFB					= strToBool(dkCH.rc(app, app, 'ffb', 'True'))						# ingame conf
dkPedalsSettingsFullThrottle		= int(dkCH.rc(app, app, 'fullthrottle', '2'))
dkPedalsSettingsFFBClip				= int(dkCH.rc(app, app, 'ffbclip', '2'))
dkPedalsSettingsSteering			= strToBool(dkCH.rc(app, app, 'steering', 'False'))					# ingame conf
dkPedalsSettingsSteeringBlinking	= strToBool(dkCH.rc(app, app, 'steeringblink', 'True'))				# ingame conf

dkPedalsSettingsHeight				= int(dkCH.rc(app, app+'Sizes', 'height', '120'))					# ingame conf
dkPedalsSettingsWidth				= int(dkCH.rc(app, app+'Sizes', 'width', '25'))						# ingame conf
dkPedalsSettingsXSpacing			= int(dkCH.rc(app, app+'Sizes', 'xspacing', '5'))					# ingame conf
dkPedalsSettingsYOffset				= int(dkCH.rc(app, app+'Sizes', 'yoffset', '0'))
dkPedalsSettingsPedalLabelFontSize	= int(dkCH.rc(app, app+'Labels', 'pedallabelfontsize', '10'))		# ingame conf
dkPedalsSettingsPedalLabelActive	= strToBool(dkCH.rc(app, app+'Labels', 'pedallabelactive', 'True'))	# ingame conf

dkPedalsSettingsHide				= strToBool(dkCH.rc(app, app+'Hide', 'hide', 'False'))				# ingame conf
dkPedalsSettingsAutohide			= strToBool(dkCH.rc(app, app+'Hide', 'autohide', 'False'))			# ingame conf
#dkPedalsSettingsFFBthresholdlow		= float(dkCH.rc(app, app+'Hide', 'ffbthresholdlow', '0.005'))

dkPedalsSettingsTurbolabel			= strToBool(dkCH.rc(app, app+'Labels', 'turbolabel', 'False'))		# ingame conf
dkPedalsSettingsFFBlabel			= strToBool(dkCH.rc(app, app+'Labels', 'ffblabel', 'False'))		# ingame conf
dkPedalsSettingsTurboPsi			= strToBool(dkCH.rc(app, app+'Labels', 'turbolabelpsi', 'False'))	# ingame conf

###########################################################
# Check if AC patch is installed
try:
	ac.ext_getHandbrake
	dkPedalsSettingsHandbrakeINSTALLED = True
	logmessage = "["+app+"] AC patch installed."
except:
	dkPedalsSettingsHandbrakeINSTALLED = False
	dkPedalsSettingsHandbrake = False
	logmessage = "["+app+"] AC patch not installed, disabling handbrake support. ( https://acstuff.ru/patch/ )"
ac.console(logmessage)
ac.log(logmessage)
###########################################################

if dkPedalsSettingsHandbrake == True and dkPedalsSettingsHandbrakeINSTALLED == False:
	dkPedalsSettingsHandbrake = False

ac.log("["+app+"] Configuration applied...")

appWindow				= 0
dkPedalsConfigButtonTimer = 0
configWindowXOffset		= -200
configWindowYOffset		= -50
configWindowVisible 	= False

steeringmax				= 60 # Must not be zero (division by zero)
turbomax				= 0.00001 # Must not be zero (division by zero)
clutchmax				= 0.00001 # Must not be zero (division by zero)
handbrakemax			= 0.00001 # Must not be zero (division by zero)
ffbmax					= 0.00001 # Must not be zero (division by zero)

def acMain(ac_version):
	global appWindow, app
	global dkPedalsLabelTurbo0, dkPedalsLabelTurbo1, dkPedalsLabelTurbo2, dkPedalsLabelTurbo3, dkPedalsLabelTurbo4, dkPedalsLabelFFB0, dkPedalsLabelFFB1, dkPedalsLabelFFB2, dkPedalsLabelFFB3, dkPedalsLabelFFB4, dkPedalsConfigButton, dkPedalsSettingsWidth

	global dkPedalsConfigBackground, dkPedalsSettingsConfigLabel
	global dkPedalsSettingsWidthLabel, dkPedalsSettingsWidthLabelActual, dkPedalsSettingsWidthIncrease, dkPedalsSettingsWidthDecrease
	global dkPedalsSettingsSpacingLabel, dkPedalsSettingsSpacingLabelActual, dkPedalsSettingsSpacingIncrease, dkPedalsSettingsSpacingDecrease
	global dkPedalsSettingsHeightLabel, dkPedalsSettingsHeightLabelActual, dkPedalsSettingsHeightIncrease, dkPedalsSettingsHeightDecrease
	global dkPedalsSettingsThrottleCheckbox, dkPedalsSettingsBrakeCheckbox, dkPedalsSettingsClutchCheckbox, dkPedalsSettingsHandbrakeCheckbox, dkPedalsSettingsFFBCheckbox, dkPedalsSettingsTurboCheckbox, dkPedalsSettingsHideCheckbox, dkPedalsSettingsAutohideCheckbox
	global dkPedalsSettingsTurboLabelCheckbox, dkPedalsSettingsFFBLabelCheckbox, dkPedalsSettingsTurboPsiCheckbox
	global dkPedalsSettingsSteeringCheckbox, dkPedalsSettingsSteeringBlinkingCheckbox
	global dkPedalsLabelClutch, dkPedalsLabelBrake, dkPedalsLabelThrottle, dkPedalsLabelHandbrake, dkPedalsLabelTurbo, dkPedalsLabelFFB, dkPedalsSettingsPedalLabelFontSize, dkPedalsSettingsPedalLabelActive, dkPedalsSettingsPedalLabelActiveCheckbox
	global dkPedalsSettingsPedalLabelFontSizeLabel, dkPedalsSettingsPedalLabelFontSizeLabelActual, dkPedalsSettingsPedalLabelFontSizeIncrease, dkPedalsSettingsPedalLabelFontSizeDecrease
	global dkPedalsSettingsPedalLabelActiveCheckbox

	neededSpace = 0

	appWindow = ac.newApp(app)
	ac.setTitle(appWindow, "")
	ac.setSize(appWindow, (dkPedalsSettingsWidth*5)+(5*dkPedalsSettingsXSpacing), dkPedalsSettingsYOffset+dkPedalsSettingsHeight)
	ac.setIconPosition(appWindow, 0, -10000)
	ac.setBackgroundOpacity(appWindow, 0)
	ac.drawBorder(appWindow, 0)
	ac.initFont(0, "consola", 0, 0)

	### Config window
	ac.addOnClickedListener(appWindow, appClick)

	# Configure button
	dkPedalsConfigButton = ac.addButton(appWindow, "Configure "+app);
	ac.setBackgroundColor(dkPedalsConfigButton, 0, 0, 0)
	ac.drawBackground(dkPedalsConfigButton, 1)
	ac.setVisible(dkPedalsConfigButton, 0)
	ac.setFontAlignment(dkPedalsConfigButton, "center")
	ac.drawBorder(dkPedalsConfigButton, 1)
	ac.setFontColor(dkPedalsConfigButton, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsConfigButton, 14)
	ac.setSize(dkPedalsConfigButton, 130, 20)
	ac.setPosition(dkPedalsConfigButton, 2, -24)
	ac.addOnClickedListener(dkPedalsConfigButton, dkPedalsConfigButtonClick)

	# Configuration background
	dkPedalsConfigBackground = ac.addButton(appWindow, "")
	ac.setBackgroundColor(dkPedalsConfigBackground, 0, 0, 0)
	ac.setVisible(dkPedalsConfigBackground, 0)	
	ac.setBackgroundOpacity(dkPedalsConfigBackground, 0.8)
	ac.drawBorder(dkPedalsConfigBackground, 0)
	ac.drawBackground(dkPedalsConfigBackground, 1)
	ac.setSize(dkPedalsConfigBackground, 170, 400)
	ac.setPosition(dkPedalsConfigBackground, configWindowXOffset-3, configWindowYOffset+0)

	# Configuration background label
	dkPedalsSettingsConfigLabel = ac.addLabel(appWindow, app)
	ac.setFontColor(dkPedalsSettingsConfigLabel, 1, 1, 1, 1)
	ac.setFontAlignment(dkPedalsSettingsConfigLabel, "left")
	ac.setFontSize(dkPedalsSettingsConfigLabel, 18)
	ac.setPosition(dkPedalsSettingsConfigLabel, configWindowXOffset+50, configWindowYOffset+0)
	ac.setVisible(dkPedalsSettingsConfigLabel, 0)	

	##########################################################################################################
	# Bar width
	neededSpace += 25
	dkPedalsSettingsWidthLabel = ac.addLabel(appWindow, "Bar width")
	ac.setBackgroundOpacity(dkPedalsSettingsWidthLabel, 0)
	ac.setVisible(dkPedalsSettingsWidthLabel, 0)
	ac.setFontAlignment(dkPedalsSettingsWidthLabel, "left")
	ac.drawBorder(dkPedalsSettingsWidthLabel, 0)
	ac.setFontColor(dkPedalsSettingsWidthLabel, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsWidthLabel, 16)
	ac.setSize(dkPedalsSettingsWidthLabel, 90, 20)
	ac.setPosition(dkPedalsSettingsWidthLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkPedalsSettingsWidthLabelActual = ac.addLabel(appWindow, "("+str(dkPedalsSettingsWidth)+")")
	ac.setBackgroundOpacity(dkPedalsSettingsWidthLabelActual, 0)
	ac.setVisible(dkPedalsSettingsWidthLabelActual, 0)
	ac.setFontAlignment(dkPedalsSettingsWidthLabelActual, "left")
	ac.drawBorder(dkPedalsSettingsWidthLabelActual, 0)
	ac.setFontColor(dkPedalsSettingsWidthLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsWidthLabelActual, 12)
	ac.setSize(dkPedalsSettingsWidthLabelActual, 30, 20)
	ac.setPosition(dkPedalsSettingsWidthLabelActual, configWindowXOffset+135, configWindowYOffset+neededSpace+3)

	dkPedalsSettingsWidthIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkPedalsSettingsWidthIncrease, 0)
	ac.setFontAlignment(dkPedalsSettingsWidthIncrease, "center")
	ac.drawBorder(dkPedalsSettingsWidthIncrease, 1)
	ac.setFontColor(dkPedalsSettingsWidthIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsWidthIncrease, 14)
	ac.setSize(dkPedalsSettingsWidthIncrease, 15, 20)
	ac.setPosition(dkPedalsSettingsWidthIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsWidthIncrease, dkPedalsSettingsDoWidthIncrease)

	dkPedalsSettingsWidthDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkPedalsSettingsWidthDecrease, 0)
	ac.setFontAlignment(dkPedalsSettingsWidthDecrease, "center")
	ac.drawBorder(dkPedalsSettingsWidthDecrease, 1)
	ac.setFontColor(dkPedalsSettingsWidthDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsWidthDecrease, 14)
	ac.setSize(dkPedalsSettingsWidthDecrease, 15, 20)
	ac.setPosition(dkPedalsSettingsWidthDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsWidthDecrease, dkPedalsSettingsDoWidthDecrease)
	##########################################################################################################

	##########################################################################################################
	# Bar spacing
	neededSpace += 20
	dkPedalsSettingsSpacingLabel = ac.addLabel(appWindow, "Bar spacing")
	ac.setBackgroundOpacity(dkPedalsSettingsSpacingLabel, 0)
	ac.setVisible(dkPedalsSettingsSpacingLabel, 0)
	ac.setFontAlignment(dkPedalsSettingsSpacingLabel, "left")
	ac.drawBorder(dkPedalsSettingsSpacingLabel, 0)
	ac.setFontColor(dkPedalsSettingsSpacingLabel, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsSpacingLabel, 16)
	ac.setSize(dkPedalsSettingsSpacingLabel, 90, 20)
	ac.setPosition(dkPedalsSettingsSpacingLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkPedalsSettingsSpacingLabelActual = ac.addLabel(appWindow, "("+str(dkPedalsSettingsXSpacing)+")")
	ac.setBackgroundOpacity(dkPedalsSettingsSpacingLabelActual, 0)
	ac.setVisible(dkPedalsSettingsSpacingLabelActual, 0)
	ac.setFontAlignment(dkPedalsSettingsSpacingLabelActual, "left")
	ac.drawBorder(dkPedalsSettingsSpacingLabelActual, 0)
	ac.setFontColor(dkPedalsSettingsSpacingLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsSpacingLabelActual, 12)
	ac.setSize(dkPedalsSettingsSpacingLabelActual, 30, 20)
	ac.setPosition(dkPedalsSettingsSpacingLabelActual, configWindowXOffset+135, configWindowYOffset+neededSpace+3)

	dkPedalsSettingsSpacingIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkPedalsSettingsSpacingIncrease, 0)
	ac.setFontAlignment(dkPedalsSettingsSpacingIncrease, "center")
	ac.drawBorder(dkPedalsSettingsSpacingIncrease, 1)
	ac.setFontColor(dkPedalsSettingsSpacingIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsSpacingIncrease, 14)
	ac.setSize(dkPedalsSettingsSpacingIncrease, 15, 20)
	ac.setPosition(dkPedalsSettingsSpacingIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsSpacingIncrease, dkPedalsSettingsDoSpacingIncrease)

	dkPedalsSettingsSpacingDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkPedalsSettingsSpacingDecrease, 0)
	ac.setFontAlignment(dkPedalsSettingsSpacingDecrease, "center")
	ac.drawBorder(dkPedalsSettingsSpacingDecrease, 1)
	ac.setFontColor(dkPedalsSettingsSpacingDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsSpacingDecrease, 14)
	ac.setSize(dkPedalsSettingsSpacingDecrease, 15, 20)
	ac.setPosition(dkPedalsSettingsSpacingDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsSpacingDecrease, dkPedalsSettingsDoSpacingDecrease)
	##########################################################################################################

	##########################################################################################################
	# Bar height
	neededSpace += 20
	dkPedalsSettingsHeightLabel = ac.addLabel(appWindow, "Bar height")
	ac.setBackgroundOpacity(dkPedalsSettingsHeightLabel, 0)
	ac.setVisible(dkPedalsSettingsHeightLabel, 0)
	ac.setFontAlignment(dkPedalsSettingsHeightLabel, "left")
	ac.drawBorder(dkPedalsSettingsHeightLabel, 0)
	ac.setFontColor(dkPedalsSettingsHeightLabel, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsHeightLabel, 16)
	ac.setSize(dkPedalsSettingsHeightLabel, 90, 20)
	ac.setPosition(dkPedalsSettingsHeightLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkPedalsSettingsHeightLabelActual = ac.addLabel(appWindow, "("+str(dkPedalsSettingsHeight)+")")
	ac.setBackgroundOpacity(dkPedalsSettingsHeightLabelActual, 0)
	ac.setVisible(dkPedalsSettingsHeightLabelActual, 0)
	ac.setFontAlignment(dkPedalsSettingsHeightLabelActual, "left")
	ac.drawBorder(dkPedalsSettingsHeightLabelActual, 0)
	ac.setFontColor(dkPedalsSettingsHeightLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsHeightLabelActual, 12)
	ac.setSize(dkPedalsSettingsHeightLabelActual, 30, 20)
	ac.setPosition(dkPedalsSettingsHeightLabelActual, configWindowXOffset+135, configWindowYOffset+neededSpace+3)

	dkPedalsSettingsHeightIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkPedalsSettingsHeightIncrease, 0)
	ac.setFontAlignment(dkPedalsSettingsHeightIncrease, "center")
	ac.drawBorder(dkPedalsSettingsHeightIncrease, 1)
	ac.setFontColor(dkPedalsSettingsHeightIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsHeightIncrease, 14)
	ac.setSize(dkPedalsSettingsHeightIncrease, 15, 20)
	ac.setPosition(dkPedalsSettingsHeightIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsHeightIncrease, dkPedalsSettingsDoHeightIncrease)

	dkPedalsSettingsHeightDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkPedalsSettingsHeightDecrease, 0)
	ac.setFontAlignment(dkPedalsSettingsHeightDecrease, "center")
	ac.drawBorder(dkPedalsSettingsHeightDecrease, 1)
	ac.setFontColor(dkPedalsSettingsHeightDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsHeightDecrease, 14)
	ac.setSize(dkPedalsSettingsHeightDecrease, 15, 20)
	ac.setPosition(dkPedalsSettingsHeightDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsHeightDecrease, dkPedalsSettingsDoHeightDecrease)
	##########################################################################################################

	##########################################################################################################
	# Throttle
	neededSpace += 30
	dkPedalsSettingsThrottleCheckbox = ac.addCheckBox(appWindow, "Throttle")
	ac.setValue(dkPedalsSettingsThrottleCheckbox, dkPedalsSettingsThrottle)
	ac.setVisible(dkPedalsSettingsThrottleCheckbox, 0)
	ac.setSize(dkPedalsSettingsThrottleCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsThrottleCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsThrottleCheckbox, dkPedalsSettingsDoThrottleCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Brake
	neededSpace += 18
	dkPedalsSettingsBrakeCheckbox = ac.addCheckBox(appWindow, "Brake")
	ac.setValue(dkPedalsSettingsBrakeCheckbox, dkPedalsSettingsBrake)
	ac.setVisible(dkPedalsSettingsBrakeCheckbox, 0)
	ac.setSize(dkPedalsSettingsBrakeCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsBrakeCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsBrakeCheckbox, dkPedalsSettingsDoBrakeCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Clutch
	neededSpace += 18
	dkPedalsSettingsClutchCheckbox = ac.addCheckBox(appWindow, "Clutch")
	ac.setValue(dkPedalsSettingsClutchCheckbox, dkPedalsSettingsClutch)
	ac.setVisible(dkPedalsSettingsClutchCheckbox, 0)
	ac.setSize(dkPedalsSettingsClutchCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsClutchCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsClutchCheckbox, dkPedalsSettingsDoClutchCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Handbrake
	if dkPedalsSettingsHandbrakeINSTALLED == True:
		neededSpace += 18
		dkPedalsSettingsHandbrakeCheckbox = ac.addCheckBox(appWindow, "Handbrake")
		ac.setValue(dkPedalsSettingsHandbrakeCheckbox, dkPedalsSettingsHandbrake)
		ac.setVisible(dkPedalsSettingsHandbrakeCheckbox, 0)
		ac.setSize(dkPedalsSettingsHandbrakeCheckbox, 12, 12)
		ac.setPosition(dkPedalsSettingsHandbrakeCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
		ac.addOnCheckBoxChanged(dkPedalsSettingsHandbrakeCheckbox, dkPedalsSettingsDoHandbrakeCheckbox)
	##########################################################################################################

	##########################################################################################################
	# FFB
	neededSpace += 18
	dkPedalsSettingsFFBCheckbox = ac.addCheckBox(appWindow, "FFB")
	ac.setValue(dkPedalsSettingsFFBCheckbox, dkPedalsSettingsFFB)
	ac.setVisible(dkPedalsSettingsFFBCheckbox, 0)
	ac.setSize(dkPedalsSettingsFFBCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsFFBCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsFFBCheckbox, dkPedalsSettingsDoFFBCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Turbo
	neededSpace += 18
	dkPedalsSettingsTurboCheckbox = ac.addCheckBox(appWindow, "Boost")
	ac.setValue(dkPedalsSettingsTurboCheckbox, dkPedalsSettingsTurbo)
	ac.setVisible(dkPedalsSettingsTurboCheckbox, 0)
	ac.setSize(dkPedalsSettingsTurboCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsTurboCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsTurboCheckbox, dkPedalsSettingsDoTurboCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Hide background of bars
	neededSpace += 30
	dkPedalsSettingsHideCheckbox = ac.addCheckBox(appWindow, "Hide background")
	ac.setValue(dkPedalsSettingsHideCheckbox, dkPedalsSettingsHide)
	ac.setVisible(dkPedalsSettingsHideCheckbox, 0)
	ac.setSize(dkPedalsSettingsHideCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsHideCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsHideCheckbox, dkPedalsSettingsDoHideCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Auto hide background of pedals when not used
	neededSpace += 18
	dkPedalsSettingsAutohideCheckbox = ac.addCheckBox(appWindow, "Autohide backgr.")
	ac.setValue(dkPedalsSettingsAutohideCheckbox, dkPedalsSettingsAutohide)
	ac.setVisible(dkPedalsSettingsAutohideCheckbox, 0)
	ac.setSize(dkPedalsSettingsAutohideCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsAutohideCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsAutohideCheckbox, dkPedalsSettingsDoAutohideCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Turbo label
	neededSpace += 18
	dkPedalsSettingsTurboLabelCheckbox = ac.addCheckBox(appWindow, "Boost label")
	ac.setValue(dkPedalsSettingsTurboLabelCheckbox, dkPedalsSettingsTurbolabel)
	ac.setVisible(dkPedalsSettingsTurboLabelCheckbox, 0)
	ac.setSize(dkPedalsSettingsTurboLabelCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsTurboLabelCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsTurboLabelCheckbox, dkPedalsSettingsDoTurboLabelCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Turbo bar or psi
	neededSpace += 18
	dkPedalsSettingsTurboPsiCheckbox = ac.addCheckBox(appWindow, "Show boost as psi")
	ac.setValue(dkPedalsSettingsTurboPsiCheckbox, dkPedalsSettingsTurboPsi)
	ac.setVisible(dkPedalsSettingsTurboPsiCheckbox, 0)
	ac.setSize(dkPedalsSettingsTurboPsiCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsTurboPsiCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsTurboPsiCheckbox, dkPedalsSettingsDoTurboPsiCheckbox)
	##########################################################################################################

	##########################################################################################################
	# FFB label
	neededSpace += 18
	dkPedalsSettingsFFBLabelCheckbox = ac.addCheckBox(appWindow, "FFB label")
	ac.setValue(dkPedalsSettingsFFBLabelCheckbox, dkPedalsSettingsFFBlabel)
	ac.setVisible(dkPedalsSettingsFFBLabelCheckbox, 0)
	ac.setSize(dkPedalsSettingsFFBLabelCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsFFBLabelCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsFFBLabelCheckbox, dkPedalsSettingsDoFFBLabelCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Pedal text labels
	neededSpace += 18
	dkPedalsSettingsPedalLabelActiveCheckbox = ac.addCheckBox(appWindow, "Text on pedals")
	ac.setValue(dkPedalsSettingsPedalLabelActiveCheckbox, dkPedalsSettingsPedalLabelActive)
	ac.setVisible(dkPedalsSettingsPedalLabelActiveCheckbox, 0)
	ac.setSize(dkPedalsSettingsPedalLabelActiveCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsPedalLabelActiveCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsPedalLabelActiveCheckbox, dkPedalsSettingsDoPedalLabelActiveCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Pedal text labels font size
	neededSpace += 25
	dkPedalsSettingsPedalLabelFontSizeLabel = ac.addLabel(appWindow, "Pedal text size")
	ac.setBackgroundOpacity(dkPedalsSettingsPedalLabelFontSizeLabel, 0)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeLabel, 0)
	ac.setFontAlignment(dkPedalsSettingsPedalLabelFontSizeLabel, "left")
	ac.drawBorder(dkPedalsSettingsPedalLabelFontSizeLabel, 0)
	ac.setFontColor(dkPedalsSettingsPedalLabelFontSizeLabel, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsPedalLabelFontSizeLabel, 16)
	ac.setSize(dkPedalsSettingsPedalLabelFontSizeLabel, 90, 20)
	ac.setPosition(dkPedalsSettingsPedalLabelFontSizeLabel, configWindowXOffset+37, configWindowYOffset+neededSpace)

	dkPedalsSettingsPedalLabelFontSizeLabelActual = ac.addLabel(appWindow, "("+str(dkPedalsSettingsPedalLabelFontSize)+")")
	ac.setBackgroundOpacity(dkPedalsSettingsPedalLabelFontSizeLabelActual, 0)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeLabelActual, 0)
	ac.setFontAlignment(dkPedalsSettingsPedalLabelFontSizeLabelActual, "left")
	ac.drawBorder(dkPedalsSettingsPedalLabelFontSizeLabelActual, 0)
	ac.setFontColor(dkPedalsSettingsPedalLabelFontSizeLabelActual, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsPedalLabelFontSizeLabelActual, 12)
	ac.setSize(dkPedalsSettingsPedalLabelFontSizeLabelActual, 30, 20)
	ac.setPosition(dkPedalsSettingsPedalLabelFontSizeLabelActual, configWindowXOffset+140, configWindowYOffset+neededSpace+3)

	dkPedalsSettingsPedalLabelFontSizeIncrease = ac.addButton(appWindow, "+")
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeIncrease, 0)
	ac.setFontAlignment(dkPedalsSettingsPedalLabelFontSizeIncrease, "center")
	ac.drawBorder(dkPedalsSettingsPedalLabelFontSizeIncrease, 1)
	ac.setFontColor(dkPedalsSettingsPedalLabelFontSizeIncrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsPedalLabelFontSizeIncrease, 14)
	ac.setSize(dkPedalsSettingsPedalLabelFontSizeIncrease, 15, 20)
	ac.setPosition(dkPedalsSettingsPedalLabelFontSizeIncrease, configWindowXOffset+18, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsPedalLabelFontSizeIncrease, dkPedalsSettingsDoPedalLabelFontSizeIncrease)

	dkPedalsSettingsPedalLabelFontSizeDecrease = ac.addButton(appWindow, "-")
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeDecrease, 0)
	ac.setFontAlignment(dkPedalsSettingsPedalLabelFontSizeDecrease, "center")
	ac.drawBorder(dkPedalsSettingsPedalLabelFontSizeDecrease, 1)
	ac.setFontColor(dkPedalsSettingsPedalLabelFontSizeDecrease, 1, 1, 1, 1)
	ac.setFontSize(dkPedalsSettingsPedalLabelFontSizeDecrease, 14)
	ac.setSize(dkPedalsSettingsPedalLabelFontSizeDecrease, 15, 20)
	ac.setPosition(dkPedalsSettingsPedalLabelFontSizeDecrease, configWindowXOffset, configWindowYOffset+neededSpace+1)
	ac.addOnClickedListener(dkPedalsSettingsPedalLabelFontSizeDecrease, dkPedalsSettingsDoPedalLabelFontSizeDecrease)
	##########################################################################################################

	##########################################################################################################
	# Steering wheel input
	neededSpace += 30
	dkPedalsSettingsSteeringCheckbox = ac.addCheckBox(appWindow, "Steering input")
	ac.setValue(dkPedalsSettingsSteeringCheckbox, dkPedalsSettingsSteering)
	ac.setVisible(dkPedalsSettingsSteeringCheckbox, 0)
	ac.setSize(dkPedalsSettingsSteeringCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsSteeringCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsSteeringCheckbox, dkPedalsSettingsDoSteeringCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Steering wheel blinking
	neededSpace += 18
	dkPedalsSettingsSteeringBlinkingCheckbox = ac.addCheckBox(appWindow, "Steering blink")
	ac.setValue(dkPedalsSettingsSteeringBlinkingCheckbox, dkPedalsSettingsSteeringBlinking)
	ac.setVisible(dkPedalsSettingsSteeringBlinkingCheckbox, 0)
	ac.setSize(dkPedalsSettingsSteeringBlinkingCheckbox, 12, 12)
	ac.setPosition(dkPedalsSettingsSteeringBlinkingCheckbox, configWindowXOffset+11, configWindowYOffset+neededSpace)
	ac.addOnCheckBoxChanged(dkPedalsSettingsSteeringBlinkingCheckbox, dkPedalsSettingsDoSteeringBlinkingCheckbox)
	##########################################################################################################

	##########################################################################################################
	# Pedal labels
	dkPedalsLabelClutch = ac.addLabel(appWindow, newlineString("CLUTCH"));
	pedalLabels(dkPedalsLabelClutch, dkPedalsSettingsPedalLabelFontSize)
	dkPedalsLabelBrake = ac.addLabel(appWindow, newlineString("BRAKE"));
	pedalLabels(dkPedalsLabelBrake, dkPedalsSettingsPedalLabelFontSize)
	dkPedalsLabelThrottle = ac.addLabel(appWindow, newlineString("THROTTLE"));
	pedalLabels(dkPedalsLabelThrottle, dkPedalsSettingsPedalLabelFontSize)
	dkPedalsLabelHandbrake = ac.addLabel(appWindow, newlineString("HANDBRAKE"));
	pedalLabels(dkPedalsLabelHandbrake, dkPedalsSettingsPedalLabelFontSize)
	dkPedalsLabelTurbo = ac.addLabel(appWindow, newlineString("BOOST"));
	pedalLabels(dkPedalsLabelTurbo, dkPedalsSettingsPedalLabelFontSize)
	dkPedalsLabelFFB = ac.addLabel(appWindow, newlineString("FFB"));
	pedalLabels(dkPedalsLabelFFB, dkPedalsSettingsPedalLabelFontSize)
	##########################################################################################################
	
	dkPedalsLabelFFB1 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelFFB1, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelFFB1, 14)
	dkPedalsLabelFFB2 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelFFB2, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelFFB2, 14)
	dkPedalsLabelFFB3 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelFFB3, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelFFB3, 14)
	dkPedalsLabelFFB4 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelFFB4, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelFFB4, 14)

	dkPedalsLabelFFB0 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelFFB0, 1, 1, 1, 0.8)
	ac.setFontSize(dkPedalsLabelFFB0, 14)

	dkPedalsLabelTurbo1 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelTurbo1, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelTurbo1, 14)
	dkPedalsLabelTurbo2 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelTurbo2, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelTurbo2, 14)
	dkPedalsLabelTurbo3 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelTurbo3, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelTurbo3, 14)
	dkPedalsLabelTurbo4 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelTurbo4, 0, 0, 0, 0.8)
	ac.setFontSize(dkPedalsLabelTurbo4, 14)

	dkPedalsLabelTurbo0 = ac.addLabel(appWindow, "");
	ac.setFontColor(dkPedalsLabelTurbo0, 1, 1, 1, 0.8)
	ac.setFontSize(dkPedalsLabelTurbo0, 14)

	ac.addRenderCallback(appWindow, onFormRender)
	return app


def newlineString(text):
	# Insert newline between every character
	return '\n'.join(text[i:i + 1] for i in range(0, len(text), 1))

def pedalLabels(label, size):
	fontName = "Orbitron"
	if ac.initFont(0, fontName, 0, 0) > 0:
		ac.setCustomFont(label, fontName, 0, 1)
	ac.setBackgroundOpacity(label, 0)
	ac.setVisible(label, 0)
	ac.setFontAlignment(label, "center")
	ac.drawBorder(label, 0)
	ac.setFontColor(label, 1, 1, 1, 1)
	ac.setFontSize(label, size)
	return

def acShutdown():
	global app
	ac.log("["+app+"] Closing...")

def acUpdate(deltaT):
	return

def appClick(name, state): # Show configuration button if user clicks on app window
	global app, dkPedalsConfigButton, dkPedalsConfigButtonTimer
	ac.setVisible(dkPedalsConfigButton, 1)
	dkPedalsConfigButtonTimer = time.clock()

def dkPedalsConfigButtonClick(name, state): # Show configuration window if user clicks on Configure button
	global app, dkPedalsConfigButton, dkPedalsConfigButtonTimer, configWindowVisible
	ac.setVisible(dkPedalsConfigButton, 0)
	dkPedalsConfigButtonTimer = 0 ###
	if configWindowVisible == True:
		ac.setVisible(dkPedalsConfigButton, 0)
		showConfigWindow(0)
		configWindowVisible = False
	else:
		ac.setVisible(dkPedalsConfigButton, 1)
		showConfigWindow(1)
		configWindowVisible = True

def dkPedalsSettingsDoWidthIncrease(name, state):
	global app, dkPedalsSettingsWidth, dkPedalsSettingsWidthLabelActual
	if dkPedalsSettingsWidth < 300:
		dkPedalsSettingsWidth += 1
		ac.setText(dkPedalsSettingsWidthLabelActual, "("+str(dkPedalsSettingsWidth)+")")
		dkCH.rc(app, app+'Sizes', 'width', dkPedalsSettingsWidth, 1)

def dkPedalsSettingsDoWidthDecrease(name, state):
	global app, dkPedalsSettingsWidth, dkPedalsSettingsWidthLabelActual
	if dkPedalsSettingsWidth > 5:
		dkPedalsSettingsWidth -= 1
		ac.setText(dkPedalsSettingsWidthLabelActual, "("+str(dkPedalsSettingsWidth)+")")
		dkCH.rc(app, app+'Sizes', 'width', dkPedalsSettingsWidth, 1)

def dkPedalsSettingsDoSpacingIncrease(name, state):
	global app, dkPedalsSettingsXSpacing, dkPedalsSettingsSpacingLabelActual
	if dkPedalsSettingsXSpacing < 100:
		dkPedalsSettingsXSpacing += 1
		ac.setText(dkPedalsSettingsSpacingLabelActual, "("+str(dkPedalsSettingsXSpacing)+")")
		dkCH.rc(app, app+'Sizes', 'xspacing', dkPedalsSettingsXSpacing, 1)

def dkPedalsSettingsDoSpacingDecrease(name, state):
	global app, dkPedalsSettingsXSpacing, dkPedalsSettingsSpacingLabelActual
	if dkPedalsSettingsXSpacing > 0:
		dkPedalsSettingsXSpacing -= 1
		ac.setText(dkPedalsSettingsSpacingLabelActual, "("+str(dkPedalsSettingsXSpacing)+")")
		dkCH.rc(app, app+'Sizes', 'xspacing', dkPedalsSettingsXSpacing, 1)

def dkPedalsSettingsDoHeightIncrease(name, state):
	global app, dkPedalsSettingsHeight, dkPedalsSettingsHeightLabelActual
	if dkPedalsSettingsHeight < 300:
		dkPedalsSettingsHeight += 1
		ac.setText(dkPedalsSettingsHeightLabelActual, "("+str(dkPedalsSettingsHeight)+")")
		dkCH.rc(app, app+'Sizes', 'height', dkPedalsSettingsHeight, 1)

def dkPedalsSettingsDoHeightDecrease(name, state):
	global app, dkPedalsSettingsHeight
	if dkPedalsSettingsHeight > 5:
		dkPedalsSettingsHeight -= 1
		ac.setText(dkPedalsSettingsHeightLabelActual, "("+str(dkPedalsSettingsHeight)+")")
		dkCH.rc(app, app+'Sizes', 'height', dkPedalsSettingsHeight, 1)

def dkPedalsSettingsDoThrottleCheckbox(name, state):
	global app, dkPedalsSettingsThrottle
	if state == 1:
		dkCH.rc(app, app, 'throttle', "True", 1)
		dkPedalsSettingsThrottle = True
	else:
		dkCH.rc(app, app, 'throttle', "False", 1)
		dkPedalsSettingsThrottle = False
		ac.setVisible(dkPedalsLabelThrottle, 0)

def dkPedalsSettingsDoBrakeCheckbox(name, state):
	global app, dkPedalsSettingsBrake
	if state == 1:
		dkCH.rc(app, app, 'brake', "True", 1)
		dkPedalsSettingsBrake = True
	else:
		dkCH.rc(app, app, 'brake', "False", 1)
		dkPedalsSettingsBrake = False
		ac.setVisible(dkPedalsLabelBrake, 0)

def dkPedalsSettingsDoClutchCheckbox(name, state):
	global app, dkPedalsSettingsClutch
	if state == 1:
		dkCH.rc(app, app, 'clutch', "True", 1)
		dkPedalsSettingsClutch = True
	else:
		dkCH.rc(app, app, 'clutch', "False", 1)
		dkPedalsSettingsClutch = False
		ac.setVisible(dkPedalsLabelClutch, 0)

def dkPedalsSettingsDoHandbrakeCheckbox(name, state):
	global app, dkPedalsSettingsHandbrake
	if state == 1:
		dkCH.rc(app, app, 'handbrake', "True", 1)
		dkPedalsSettingsHandbrake = True
	else:
		dkCH.rc(app, app, 'handbrake', "False", 1)
		dkPedalsSettingsHandbrake = False
		ac.setVisible(dkPedalsLabelHandbrake, 0)

def dkPedalsSettingsDoFFBCheckbox(name, state):
	global app, dkPedalsSettingsFFB
	if state == 1:
		dkCH.rc(app, app, 'ffb', "True", 1)
		dkPedalsSettingsFFB = True
	else:
		dkCH.rc(app, app, 'ffb', "False", 1)
		dkPedalsSettingsFFB = False
		ac.setVisible(dkPedalsLabelFFB, 0)

def dkPedalsSettingsDoTurboCheckbox(name, state):
	global app, dkPedalsSettingsTurbo
	if state == 1:
		dkCH.rc(app, app, 'turbo', "True", 1)
		dkPedalsSettingsTurbo = True
	else:
		dkCH.rc(app, app, 'turbo', "False", 1)
		dkPedalsSettingsTurbo = False
		ac.setVisible(dkPedalsLabelTurbo, 0)

def dkPedalsSettingsDoHideCheckbox(name, state):
	global app, dkPedalsSettingsHide
	if state == 1:
		dkCH.rc(app, app+'Hide', 'hide', "True", 1)
		dkPedalsSettingsHide = True
	else:
		dkCH.rc(app, app+'Hide', 'hide', "False", 1)
		dkPedalsSettingsHide = False

def dkPedalsSettingsDoAutohideCheckbox(name, state):
	global app, dkPedalsSettingsAutohide
	if state == 1:
		dkCH.rc(app, app+'Hide', 'autohide', "True", 1)
		dkPedalsSettingsAutohide = True
	else:
		dkCH.rc(app, app+'Hide', 'autohide', "False", 1)
		dkPedalsSettingsAutohide = False

def dkPedalsSettingsDoTurboLabelCheckbox(name, state):
	global app, dkPedalsSettingsTurbolabel
	if state == 1:
		dkCH.rc(app, app+'Labels', 'turbolabel', "True", 1)
		dkPedalsSettingsTurbolabel = True
	else:
		dkCH.rc(app, app+'Labels', 'turbolabel', "False", 1)
		dkPedalsSettingsTurbolabel = False
		updateText("dkPedalsLabelTurbo", "")

def dkPedalsSettingsDoTurboPsiCheckbox(name, state):
	global app, dkPedalsSettingsTurboPsi
	if state == 1:
		dkCH.rc(app, app+'Labels', 'turbolabelpsi', "True", 1)
		dkPedalsSettingsTurboPsi = True
	else:
		dkCH.rc(app, app+'Labels', 'turbolabelpsi', "False", 1)
		dkPedalsSettingsTurboPsi = False

def dkPedalsSettingsDoFFBLabelCheckbox(name, state):
	global app, dkPedalsSettingsFFBlabel
	if state == 1:
		dkCH.rc(app, app+'Labels', 'ffblabel', "True", 1)
		dkPedalsSettingsFFBlabel = True
	else:
		dkCH.rc(app, app+'Labels', 'ffblabel', "False", 1)
		dkPedalsSettingsFFBlabel = False
		updateText("dkPedalsLabelFFB", "")

def dkPedalsSettingsDoPedalLabelActiveCheckbox(name, state):
	global app, dkPedalsSettingsPedalLabelActive
	if state == 1:
		dkCH.rc(app, app+'Labels', 'pedallabelactive', "True", 1)
		dkPedalsSettingsPedalLabelActive = True
	else:
		dkCH.rc(app, app+'Labels', 'pedallabelactive', "False", 1)
		dkPedalsSettingsPedalLabelActive = False
		ac.setVisible(dkPedalsLabelClutch, 0)
		ac.setVisible(dkPedalsLabelBrake, 0)
		ac.setVisible(dkPedalsLabelThrottle, 0)
		ac.setVisible(dkPedalsLabelHandbrake, 0)
		ac.setVisible(dkPedalsLabelTurbo, 0)
		ac.setVisible(dkPedalsLabelFFB, 0)

def dkPedalsSettingsDoPedalLabelFontSizeIncrease(name, state):
	global app, dkPedalsSettingsPedalLabelFontSize, dkPedalsSettingsPedalLabelFontSizeLabelActual
	if dkPedalsSettingsPedalLabelFontSize < 200:
		dkPedalsSettingsPedalLabelFontSize += 1
		ac.setText(dkPedalsSettingsPedalLabelFontSizeLabelActual, "("+str(dkPedalsSettingsPedalLabelFontSize)+")")
		ac.setFontSize(dkPedalsLabelClutch, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelBrake, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelThrottle, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelHandbrake, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelTurbo, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelFFB, dkPedalsSettingsPedalLabelFontSize)
		dkCH.rc(app, app+'Labels', 'pedallabelfontsize', dkPedalsSettingsPedalLabelFontSize, 1)

def dkPedalsSettingsDoPedalLabelFontSizeDecrease(name, state):
	global app, dkPedalsSettingsPedalLabelFontSize, dkPedalsSettingsPedalLabelFontSizeLabelActual
	if dkPedalsSettingsPedalLabelFontSize > 2:
		dkPedalsSettingsPedalLabelFontSize -= 1
		ac.setText(dkPedalsSettingsPedalLabelFontSizeLabelActual, "("+str(dkPedalsSettingsPedalLabelFontSize)+")")
		ac.setFontSize(dkPedalsLabelClutch, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelBrake, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelThrottle, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelHandbrake, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelTurbo, dkPedalsSettingsPedalLabelFontSize)
		ac.setFontSize(dkPedalsLabelFFB, dkPedalsSettingsPedalLabelFontSize)
		dkCH.rc(app, app+'Labels', 'pedallabelfontsize', dkPedalsSettingsPedalLabelFontSize, 1)

def dkPedalsSettingsDoSteeringCheckbox(name, state):
	global app, dkPedalsSettingsSteering
	if state == 1:
		dkCH.rc(app, app, 'steering', "True", 1)
		dkPedalsSettingsSteering = True
	else:
		dkCH.rc(app, app, 'steering', "False", 1)
		dkPedalsSettingsSteering = False

def dkPedalsSettingsDoSteeringBlinkingCheckbox(name, state):
	global app, dkPedalsSettingsSteeringBlinking
	if state == 1:
		dkCH.rc(app, app, 'steeringblink', "True", 1)
		dkPedalsSettingsSteeringBlinking = True
	else:
		dkCH.rc(app, app, 'steeringblink', "False", 1)
		dkPedalsSettingsSteeringBlinking = False

def showConfigWindow(state):
	global app
	global dkPedalsConfigBackground, dkPedalsSettingsConfigLabel
	global dkPedalsSettingsWidthLabel, dkPedalsSettingsWidthLabelActual, dkPedalsSettingsWidthIncrease, dkPedalsSettingsWidthDecrease
	global dkPedalsSettingsSpacingLabel, dkPedalsSettingsSpacingLabelActual, dkPedalsSettingsSpacingIncrease, dkPedalsSettingsSpacingDecrease
	global dkPedalsSettingsHeightLabel, dkPedalsSettingsHeightLabelActual, dkPedalsSettingsHeightIncrease, dkPedalsSettingsHeightDecrease
	global dkPedalsSettingsThrottleCheckbox, dkPedalsSettingsBrakeCheckbox, dkPedalsSettingsClutchCheckbox, dkPedalsSettingsHandbrakeCheckbox, dkPedalsSettingsFFBCheckbox, dkPedalsSettingsTurboCheckbox
	global dkPedalsSettingsHideCheckbox, dkPedalsSettingsAutohideCheckbox
	global dkPedalsSettingsTurboLabelCheckbox, dkPedalsSettingsFFBLabelCheckbox, dkPedalsSettingsTurboPsiCheckbox
	global dkPedalsSettingsSteeringCheckbox, dkPedalsSettingsSteeringBlinkingCheckbox
	global dkPedalsSettingsPedalLabelFontSizeLabel, dkPedalsSettingsPedalLabelFontSizeLabelActual, dkPedalsSettingsPedalLabelFontSizeIncrease, dkPedalsSettingsPedalLabelFontSizeDecrease
	global dkPedalsSettingsPedalLabelActiveCheckbox

	ac.setVisible(dkPedalsConfigBackground, state)
	ac.setVisible(dkPedalsSettingsConfigLabel, state)

	ac.setVisible(dkPedalsSettingsWidthLabel, state)
	ac.setVisible(dkPedalsSettingsWidthLabelActual, state)
	ac.setVisible(dkPedalsSettingsWidthIncrease, state)
	ac.setVisible(dkPedalsSettingsWidthDecrease, state)

	ac.setVisible(dkPedalsSettingsSpacingLabel, state)
	ac.setVisible(dkPedalsSettingsSpacingLabelActual, state)
	ac.setVisible(dkPedalsSettingsSpacingIncrease, state)
	ac.setVisible(dkPedalsSettingsSpacingDecrease, state)

	ac.setVisible(dkPedalsSettingsHeightLabel, state)
	ac.setVisible(dkPedalsSettingsHeightLabelActual, state)
	ac.setVisible(dkPedalsSettingsHeightIncrease, state)
	ac.setVisible(dkPedalsSettingsHeightDecrease, state)

	ac.setVisible(dkPedalsSettingsThrottleCheckbox, state)
	ac.setVisible(dkPedalsSettingsBrakeCheckbox, state)
	ac.setVisible(dkPedalsSettingsClutchCheckbox, state)
	ac.setVisible(dkPedalsSettingsHandbrakeCheckbox, state)
	ac.setVisible(dkPedalsSettingsFFBCheckbox, state)
	ac.setVisible(dkPedalsSettingsTurboCheckbox, state)

	ac.setVisible(dkPedalsSettingsHideCheckbox, state)
	ac.setVisible(dkPedalsSettingsAutohideCheckbox, state)

	ac.setVisible(dkPedalsSettingsTurboLabelCheckbox, state)
	ac.setVisible(dkPedalsSettingsFFBLabelCheckbox, state)
	ac.setVisible(dkPedalsSettingsTurboPsiCheckbox, state)

	ac.setVisible(dkPedalsSettingsPedalLabelActiveCheckbox, state)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeLabel, state)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeLabelActual, state)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeIncrease, state)
	ac.setVisible(dkPedalsSettingsPedalLabelFontSizeDecrease, state)

	ac.setVisible(dkPedalsSettingsSteeringCheckbox, state)
	ac.setVisible(dkPedalsSettingsSteeringBlinkingCheckbox, state)

def updateText(textLabel, content):
	# Update text and text shadows
	for xx in range(0, 5):
		ac.setText(eval(textLabel+str(xx)), content)

def onFormRender(deltaT):
	global app, appWindow, dkPedalsConfigButtonTimer, configWindowVisible, sideset, numPedals
	global turbomax, clutchmax, handbrakemax, ffbmax, dkPedalsLabelTurbo0, dkPedalsLabelTurbo1, dkPedalsLabelTurbo2, dkPedalsLabelTurbo3, dkPedalsLabelTurbo4, dkPedalsLabelFFB0, dkPedalsLabelFFB1, dkPedalsLabelFFB2, dkPedalsLabelFFB3, dkPedalsLabelFFB4
	global steeringmax
	global dkPedalsLabelThrottle

	# Handle configuration window
	if dkPedalsConfigButtonTimer > 0 and configWindowVisible == False:
		if (time.clock() - dkPedalsConfigButtonTimer) > 3:
			dkPedalsConfigButtonTimer = 0
			ac.setVisible(dkPedalsConfigButton, 0)

	ac.setBackgroundOpacity(appWindow, 0)
	carActive = 0
	carActive = ac.getFocusedCar()

	# Steering
	if dkPedalsSettingsSteering == True and 'sideset' in globals() and 'numPedals' in globals():
		steeringWidth = sideset-dkPedalsSettingsXSpacing
		blinkDegrees = 10
		steering = ac.getCarState(carActive, acsys.CS.Steer)

		addSpace = 0
		if dkPedalsSettingsTurbolabel == True or dkPedalsSettingsFFBlabel == True:
			addSpace = 14

		if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
			ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			ac.glQuad(0, addSpace+dkPedalsSettingsYOffset+dkPedalsSettingsHeight+dkPedalsSettingsXSpacing, steeringWidth, dkPedalsSettingsWidth/1.5)

		# Steering blink
		if (steering < -blinkDegrees or steering > blinkDegrees) and ac.getCarState(carActive, acsys.CS.SpeedKMH) < 1:
			if dkPedalsSettingsSteeringBlinking == True and int(round(time.time() * 10) %10) < 5:
				ac.glColor4f(1.0, 0.0, 0.0, 1.0)
				ac.glQuad(-1, addSpace+dkPedalsSettingsYOffset+dkPedalsSettingsHeight+dkPedalsSettingsXSpacing-1, steeringWidth+2, dkPedalsSettingsWidth/1.5+2)

		if abs(steering) > steeringmax:
			steeringmax = abs(steering)

		myVal = (steeringWidth/2)/steeringmax*steering
		
		if steering > 0:
			ac.glColor4f(0.0, 0.0, 0.8, 1.0)
			ac.glQuad(steeringWidth/2, addSpace+dkPedalsSettingsYOffset+dkPedalsSettingsHeight+dkPedalsSettingsXSpacing, myVal, dkPedalsSettingsWidth/1.5)
		if steering < 0:
			ac.glColor4f(0.0, 0.0, 0.8, 1.0)
			ac.glQuad(steeringWidth/2+myVal, addSpace+dkPedalsSettingsYOffset+dkPedalsSettingsHeight+dkPedalsSettingsXSpacing, -myVal, dkPedalsSettingsWidth/1.5)

	sideset = 0
	numPedals = 0

	# Clutch
	if dkPedalsSettingsClutch == True:
		clutch = 1.0-ac.getCarState(carActive, acsys.CS.Clutch)
		# Is clutch present? Demo?
		if clutch > clutchmax:
			clutchmax = clutch
		if clutchmax > 0.00001:
			if dkPedalsSettingsPedalLabelActive == True:
				ac.setPosition(dkPedalsLabelClutch, sideset+(dkPedalsSettingsWidth/2), 5) # Label
				ac.setVisible(dkPedalsLabelClutch, 1) # Label
			if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-clutch))
			elif dkPedalsSettingsHide != True and clutch > 0:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-clutch))

			if clutch > 0:
				ac.glColor4f(0.0, 0.0, 0.8, 1.0)
				ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-clutch), dkPedalsSettingsWidth, dkPedalsSettingsHeight*clutch)
			sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
			numPedals += 1

	# Brake
	if dkPedalsSettingsBrake == True:
		if dkPedalsSettingsPedalLabelActive == True:
			ac.setPosition(dkPedalsLabelBrake, sideset+(dkPedalsSettingsWidth/2), 5) # Label
			ac.setVisible(dkPedalsLabelBrake, 1) # Label
		brake = ac.getCarState(carActive, acsys.CS.Brake)
		if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
			ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-brake))
		elif dkPedalsSettingsHide != True and brake > 0:
			ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-brake))

		if brake > 0:
			ac.glColor4f(0.8, 0.0, 0.0, 1.0)
			ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-brake), dkPedalsSettingsWidth,dkPedalsSettingsHeight*brake)
		sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
		numPedals += 1

	# Throttle
	if dkPedalsSettingsThrottle == True:
		if dkPedalsSettingsPedalLabelActive == True:
			ac.setPosition(dkPedalsLabelThrottle, sideset+(dkPedalsSettingsWidth/2), 5) # Label
			ac.setVisible(dkPedalsLabelThrottle, 1) # Label
		gas = ac.getCarState(carActive, acsys.CS.Gas)
		if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
			ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-gas))
		elif dkPedalsSettingsHide != True and gas > 0:
			ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-gas))

		if gas > 0:
			# Show frame on full throttle
			if gas >= 1:
				ac.glColor4f(1.0, 1.0, 1.0, 1.0)
				ac.glQuad(sideset-dkPedalsSettingsFullThrottle, dkPedalsSettingsYOffset-dkPedalsSettingsFullThrottle+dkPedalsSettingsHeight*(1-gas), dkPedalsSettingsWidth+(dkPedalsSettingsFullThrottle*2), dkPedalsSettingsHeight*gas+(dkPedalsSettingsFullThrottle*2))

			ac.glColor4f(0.0, 0.8, 0.0, 1.0)
			ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-gas), dkPedalsSettingsWidth, dkPedalsSettingsHeight*gas)
		sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
		numPedals += 1

	# Handbrake
	if dkPedalsSettingsHandbrake == True:
		#handbrake = ac.getCarState(carActive, acsys.CS.Handbrake) # If Kunos would have made it right
		handbrake = ac.ext_getHandbrake(carActive) # AC patch
		# Is handbrake present? Demo?
		if handbrake > handbrakemax:
			handbrakemax = handbrake
		if handbrakemax > 0.00001:
			if dkPedalsSettingsPedalLabelActive == True:
				ac.setPosition(dkPedalsLabelHandbrake, sideset+(dkPedalsSettingsWidth/2), 5) # Label
				ac.setVisible(dkPedalsLabelHandbrake, 1) # Label

			if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-handbrake))
			elif dkPedalsSettingsHide != True and handbrake > 0:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-handbrake))

			if handbrake > 0:
				ac.glColor4f(0.0, 0.8, 0.8, 1.0)
				ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-handbrake), dkPedalsSettingsWidth, dkPedalsSettingsHeight*handbrake)
			sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
			numPedals += 1

	# Turbo boost
	if dkPedalsSettingsTurbo == True:
		turboValue = abs(ac.getCarState(carActive, acsys.CS.TurboBoost))
		# Set maximum turbo boost value
		if turboValue > turbomax:
			turbomax = turboValue
		turbo = turboValue/turbomax
		if turbomax > 0.00001:
			if dkPedalsSettingsPedalLabelActive == True:
				ac.setPosition(dkPedalsLabelTurbo, sideset+(dkPedalsSettingsWidth/2), 5) # Label
				ac.setVisible(dkPedalsLabelTurbo, 1) # Label
			if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-turbo))
			elif dkPedalsSettingsHide != True and turbo > 0:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-turbo))

			if turbo > 0:
				ac.glColor4f(0.8, 0.8, 0.0, 1.0)
				ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-turbo), dkPedalsSettingsWidth, dkPedalsSettingsHeight*turbo)

			if dkPedalsSettingsTurbolabel == True:
				if turboValue > 0.001:
					# Make shadow the ugly way
					ac.setPosition(dkPedalsLabelTurbo0, sideset+2, dkPedalsSettingsHeight)
					ac.setPosition(dkPedalsLabelTurbo1, sideset+3, dkPedalsSettingsHeight-1)
					ac.setPosition(dkPedalsLabelTurbo2, sideset+3, dkPedalsSettingsHeight+1)
					ac.setPosition(dkPedalsLabelTurbo3, sideset+1, dkPedalsSettingsHeight-1)
					ac.setPosition(dkPedalsLabelTurbo4, sideset+1, dkPedalsSettingsHeight+1)

					# Update text
					if dkPedalsSettingsTurboPsi == True:
						updateText("dkPedalsLabelTurbo", str(round(turboValue*14.5038, 1)))
					else:
						updateText("dkPedalsLabelTurbo", str(round(turboValue, 2)))
				else:
					updateText("dkPedalsLabelTurbo", "")

			sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
			numPedals += 1

	# Force feedback
	if dkPedalsSettingsFFB == True:
		ffb = ac.getCarState(carActive, acsys.CS.LastFF)
		# Is ffb ~0? Demo playback!?
		if ffb > ffbmax:
			ffbmax = ffb
		if ffbmax > 0.00001:

			if dkPedalsSettingsPedalLabelActive == True:
				ac.setPosition(dkPedalsLabelFFB, sideset+(dkPedalsSettingsWidth/2), 5) # Label
				ac.setVisible(dkPedalsLabelFFB, 1) # Label

			if ffb >= 1:
				ffbtemp = 1 # Set maximum ffb to show.
			else:
				ffbtemp = ffb
			
			# This is really irritating! Removed.
			#if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
			#	ac.glColor4f(0.0, 0.0, 0.0, 0.5)
			#	ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-ffb))
			#elif dkPedalsSettingsHide != True and ffb > dkPedalsSettingsFFBthresholdlow:
			if dkPedalsSettingsHide != True and dkPedalsSettingsAutohide != True:
				ac.glColor4f(0.0, 0.0, 0.0, 0.5)
				ac.glQuad(sideset, dkPedalsSettingsYOffset, dkPedalsSettingsWidth, dkPedalsSettingsHeight*(1-ffbtemp))

			if ffb > 0:
				# Show frame on FFBClip
				#if ffb >= 1:
					#ac.glColor4f(1.0, 0, 0, 1.0)
					#ac.glQuad(sideset-dkPedalsSettingsFFBClip, dkPedalsSettingsYOffset-dkPedalsSettingsFFBClip+dkPedalsSettingsHeight*(1-ffbtemp), #dkPedalsSettingsWidth+(dkPedalsSettingsFFBClip*2), dkPedalsSettingsHeight*ffbtemp+(dkPedalsSettingsFFBClip*2))
				if ffb >= 1:
					ac.glColor4f(1.0, 0.0, 0.0, 1.0)
				else:
					ac.glColor4f(0.8, 0.8, 0.8, 1.0)
				ac.glQuad(sideset, dkPedalsSettingsYOffset+dkPedalsSettingsHeight*(1-ffbtemp), dkPedalsSettingsWidth, dkPedalsSettingsHeight*ffbtemp)

			if dkPedalsSettingsFFBlabel == True:
				if ffb > 0.001:
					# Make shadow the ugly way
					ac.setPosition(dkPedalsLabelFFB0, sideset+2, dkPedalsSettingsHeight)
					ac.setPosition(dkPedalsLabelFFB1, sideset+3, dkPedalsSettingsHeight-1)
					ac.setPosition(dkPedalsLabelFFB2, sideset+3, dkPedalsSettingsHeight+1)
					ac.setPosition(dkPedalsLabelFFB3, sideset+1, dkPedalsSettingsHeight-1)
					ac.setPosition(dkPedalsLabelFFB4, sideset+1, dkPedalsSettingsHeight+1)

					# Update text
					updateText("dkPedalsLabelFFB", str(round(ffb, 2)))
				else:
					updateText("dkPedalsLabelFFB", "")

			sideset += dkPedalsSettingsWidth+dkPedalsSettingsXSpacing
			numPedals += 1
