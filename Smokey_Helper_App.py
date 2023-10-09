import ac
import sol_UI as ui

appName = "AC Drift Setup Helper"
width, height = 400, 800

def acMain(ac_version):
    appWindow = ac.newApp(appName)
    ac.setSize(appWindow, width, height)
    ac.setTitle(appWindow, appName)

    yOffset = 10
    labelHeight = 20
    progressBarHeight = 20
    spacing = 10
    dropdownHeight = 30

    def addLabelAndProgressBar(title, min_val, max_val, default_val):
        nonlocal yOffset
        label = ui.label(appWindow, title, 10, yOffset, width-20, labelHeight)
        yOffset += labelHeight + spacing
        progressBar = ui.hslider(appWindow, 10, yOffset, width-20, progressBarHeight, min_val, max_val, default_val)
        yOffset += progressBarHeight + spacing
        return progressBar

    def addLabelAndDropdown(title, items):
        nonlocal yOffset
        label = ui.label(appWindow, title, 10, yOffset, width-20, labelHeight)
        yOffset += labelHeight + spacing
        dropdown = ui.listbox(appWindow, 10, yOffset, width-20, dropdownHeight)
        for item in items:
            ac.addItem(dropdown, item)
        yOffset += dropdownHeight + spacing
        return dropdown

    # UI Elements
    tirePressureProgressBar = addLabelAndProgressBar("Tire Pressure (psi)", 20, 40, 30)
    suspensionStiffnessProgressBar = addLabelAndProgressBar("Suspension Stiffness (1-10)", 1, 10, 5)
    brakeBiasProgressBar = addLabelAndProgressBar("Brake Bias (F/R %)", 30, 70, 50)
    turboBoostProgressBar = addLabelAndProgressBar("Turbo Boost (%)", 0, 100, 50)
    differentialSettingDropdown = addLabelAndDropdown("Differential Setting", ["Open", "Semi-Locked", "Locked"])
    tireCompoundDropdown = addLabelAndDropdown("Tire Compound", ["Soft", "Medium", "Hard"])
    camberSettingProgressBar = addLabelAndProgressBar("Camber Setting", -5, 5, 0)
    toeSettingProgressBar = addLabelAndProgressBar("Toe Setting", -5, 5, 0)
    handbrakeSensitivityProgressBar = addLabelAndProgressBar("Handbrake Sensitivity", 0, 100, 50)
    weightDistributionProgressBar = addLabelAndProgressBar("Weight Distribution", 40, 60, 50)
    aeroSettingProgressBar = addLabelAndProgressBar("Aero Setting", 0, 100, 50)

    return appName

def acUpdate(deltaT):
    pass

def acShutdown():
    pass
