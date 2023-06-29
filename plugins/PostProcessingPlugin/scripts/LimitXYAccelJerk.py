# Limit XY Accel:  Authored by: Greg Foresi (GregValiant)
# July 2023
# Sometimes bed-slinger printers need different Accel and Jerk values for the Y but Cura always makes them the same.
# This script changes the Accel and/or Jerk from the beginning of the 'Start Layer' to the end of the 'End Layer'.
# The existing M201 Max Accel will be changed to limit the Y (and/or X) accel at the printer.  If you have Accel enabled in Cura and the XY Accel is set to 3000 then setting the Y limit to 1000 will result in the printer limiting the Y to 1000.  This can keep tall skinny prints from breaking loose of the bed and failing.  The script was not tested with Junction Deviation.
# If enabled - the Jerk setting is changed line-by-line within the gcode as there is no "limit" on Jerk.
# if 'Gradual ACCEL change' is enabled then the Accel is changed gradually from the Start to the End layer and that will be the final Accel setting in the file.  If 'Gradual' is enabled then the Jerk settings will continue to be changed to the end of the file (rather than ending at the End layer).

from ..Script import Script
from cura.CuraApplication import CuraApplication
import re

class LimitXYAccelJerk(Script):
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        super().initialize()
        # Get the Accel and Jerk and set the values in the setting boxes---------------------------------------------    
        mycura = CuraApplication.getInstance().getGlobalContainerStack()
        extruder = mycura.extruderList
        accel_print = extruder[0].getProperty("acceleration_print", "value")
        accel_travel = extruder[0].getProperty("acceleration_travel", "value")
        jerk_print_old = extruder[0].getProperty("jerk_print", "value")
        jerk_travel_old = extruder[0].getProperty("jerk_travel", "value")
        self._instance.setProperty("X_accel_limit", "value", round(accel_print))
        self._instance.setProperty("Y_accel_limit", "value", round(accel_print))
        self._instance.setProperty("X_jerk", "value", jerk_print_old)
        self._instance.setProperty("Y_jerk", "value", jerk_print_old)
 
    def getSettingDataString(self):
            return """{
            "name": "Limit the X-Y Accel/Jerk",
            "key": "LimitXYAccelJerk",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "X_accel_limit":
                {
                    "label": "X MAX Acceleration",
                    "description": "If this number is lower than the 'X Print Accel' in Cura then this will limit the Accel on the X axis.  Enter the Maximum Acceleration value for the X axis.  This will affect both Print and Travel Accel.  If you enable an End Layer then at the end of that layer the Accel Limit will be reset (unless you choose 'Gradual' in which case the new limit goes to the top layer).",
                    "type": "int",
                    "enabled": true,
                    "minimum_value": 50,
                    "unit": "mm/sec² ",
                    "default_value": 500
                },
                "Y_accel_limit":
                {
                    "label": "Y MAX Acceleration",
                    "description": "If this number is lower than the Y accel in Cura then this will limit the Accel on the Y axis.  Enter the Maximum Acceleration value for the Y axis.  This will affect both Print and Travel Accel.  If you enable an End Layer then at the end of that layer the Accel Limit will be reset (unless you choose 'Gradual' in which case the new limit goes to the top layer).",
                    "type": "int",
                    "enabled": true,
                    "minimum_value": 50,
                    "unit": "mm/sec² ",
                    "default_value": 500
                },
                "jerk_enable":
                {
                    "label": "Change the Jerk",
                    "description": "Whether to change the Jerk values.",
                    "type": "bool",
                    "enabled": true,
                    "default_value": false
                },
                "X_jerk":
                {
                    "label": "    X jerk",
                    "description": "Enter the Jerk value for the X axis.  Enter '0' to use the existing X Jerk.  This setting will affect both the Print and Travel jerk.",
                    "type": "int",
                    "enabled": "jerk_enable",
                    "unit": "mm/sec ",
                    "default_value": 8
                },
                "Y_jerk":
                {
                    "label": "    Y jerk",
                    "description": "Enter the Jerk value for the Y axis. Enter '0' to use the existing Y Jerk.    This setting will affect both the Print and Travel jerk.",
                    "type": "int",
                    "enabled": "jerk_enable",
                    "unit": "mm/sec ",
                    "default_value": 8
                },
                "start_layer":
                {
                    "label": "From Start of Layer:",
                    "description": "Use the Cura Preview numbers. Enter the Layer to start the changes at. The minimum is Layer 1.",
                    "type": "int",
                    "default_value": 1,
                    "minimum_value": 1,
                    "unit": "Lay# ",
                    "enabled": "not gradient_change"
                },
                "end_layer":
                {
                    "label": "To End of Layer",
                    "description": "Use the Cura Preview numbers. Enter '-1' for the entire file or enter a layer number.  The changes will end at your 'End Layer' and revert back to the original numbers.",
                    "type": "int",
                    "default_value": -1,
                    "minimum_value": -1,
                    "unit": "Lay# ",
                    "enabled": "not gradient_change"
                },
                "gradient_change":
                {
                    "label": "Gradual ACCEL Change",
                    "description": "Gradually change the Accel numbers 'From layer' - 'To Layer'.  If Jerk is enabled the Jerk changes are not 'Gradual' because there is no Max Jerk setting.  Unlike Constant change - using 'Gradual' the Accel and Jerk change continues from the End Layer to the end of the file.",
                    "type": "bool",
                    "default_value": false,
                    "enabled": true
                },
                "gradient_start_layer":
                {
                    "label": "     Gradual From Layer:",
                    "description": "Use the Cura Preview numbers. Enter the Layer to start the changes at. The minimum is Layer 1.",
                    "type": "int",
                    "default_value": 1,
                    "minimum_value": 1,
                    "unit": "Lay# ",
                    "enabled": "gradient_change"
                },
                "gradient_end_layer":
                {
                    "label": "     Gradual To Layer",
                    "description": "Use the Cura Preview numbers. Enter '-1' for the top layer or enter a layer number.  The last 'Gradual' change will continue to the end of the file.",
                    "type": "int",
                    "default_value": -1,
                    "minimum_value": -1,
                    "unit": "Lay# ",
                    "enabled": "gradient_change"
                }
            }
        }"""

    def execute(self, data):
        mycura = CuraApplication.getInstance().getGlobalContainerStack()
        extruder = mycura.extruderList
        constant_change = not bool(self.getSettingValueByKey("gradient_change"))
        accel_print_enabled = bool(extruder[0].getProperty("acceleration_enabled", "value"))
        accel_travel_enabled = bool(extruder[0].getProperty("acceleration_travel_enabled", "value"))
        accel_print = extruder[0].getProperty("acceleration_print", "value")
        accel_travel = extruder[0].getProperty("acceleration_travel", "value")
        jerk_print_enabled = str(extruder[0].getProperty("jerk_enabled", "value"))
        jerk_travel_enabled = str(extruder[0].getProperty("jerk_travel_enabled", "value"))
        jerk_print_old = extruder[0].getProperty("jerk_print", "value")
        jerk_travel_old = extruder[0].getProperty("jerk_travel", "value")
        if int(accel_print) >= int(accel_travel):
            accel_old = accel_print
        else:
            accel_old = accel_travel
        jerk_travel = str(extruder[0].getProperty("jerk_travel", "value"))
        if int(jerk_print_old) >= int(jerk_travel_old):
            jerk_old = jerk_print_old
        else:
            jerk_old = jerk_travel_old

        #Set the new Accel values---------------------------------------------------------------------------------
        x_accel = str(self.getSettingValueByKey("X_accel_limit"))
        y_accel = str(self.getSettingValueByKey("Y_accel_limit"))
        x_jerk = int(self.getSettingValueByKey("X_jerk"))  
        y_jerk = int(self.getSettingValueByKey("Y_jerk"))
        # Put the strings together
        M201_limit_new = "M201 X" + x_accel + " Y" + y_accel
        M201_limit_old = "M201 X" + str(round(accel_old)) + " Y" + str(round(accel_old))
        if x_jerk == 0:
            M205_jerk_pattern = "Y(\d*)"
            M205_jerk_new = "Y" + str(y_jerk)
        if y_jerk == 0:
            M205_jerk_pattern = "X(\d*)"
            M205_jerk_new = "X" + str(x_jerk)
        if x_jerk != 0 and y_jerk != 0:
            M205_jerk_pattern = "M205 X(\d*) Y(\d*)"
            M205_jerk_new = "M205 X" + str(x_jerk) + " Y" + str(y_jerk)
        M205_jerk_old = "M205 X" + str(jerk_old) + " Y" + str(jerk_old)
            
        #Get the indexes of the start and end layers----------------------------------------
        if constant_change:
            start_layer = int(self.getSettingValueByKey("start_layer"))-1
            end_layer = int(self.getSettingValueByKey("end_layer"))
        else:
            start_layer = int(self.getSettingValueByKey("gradient_start_layer"))-1
            end_layer = int(self.getSettingValueByKey("gradient_end_layer"))
        start_index = 2
        end_index = len(data)-2
        for num in range(2,len(data)-1):
            if ";LAYER:" + str(start_layer) + "\n" in data[num]:
                start_index = num
                break
        if int(end_layer) > 0:
            for num in range(3,len(data)-1):
                try:
                    if ";LAYER:" + str(end_layer) + "\n" in data[num]:
                        end_index = num
                        break
                except:
                    end_index = len(data)-2      

        #Add Accel limit and new Jerk at start layer-----------------------------------------------------
        if constant_change:
            layer = data[start_index]
            lines = layer.split("\n")
            for index, line in enumerate(lines):
                if lines[index].startswith(";LAYER:"):
                    lines.insert(index+1,M201_limit_new)
                    if self.getSettingValueByKey("jerk_enable"):
                        lines.insert(index+2,M205_jerk_new)
                    data[start_index] = "\n".join(lines)
                    break
            
            #Alter any existing jerk lines.  Accel lines can be ignored-----------------------------------  
            for num in range(start_index,end_index,1):
                layer = data[num]
                lines = layer.split("\n")
                for index, line in enumerate(lines):
                    if line.startswith("M205"):
                        lines[index] = re.sub(M205_jerk_pattern, M205_jerk_new, line)
                data[num] = "\n".join(lines)
            if end_layer != -1:
                try:
                    layer = data[end_index-1]
                    lines = layer.split("\n")
                    lines.insert(len(lines)-2,M201_limit_old)
                    lines.insert(len(lines)-2,M205_jerk_old)
                    data[end_index-1] = "\n".join(lines)
                except:
                    all
            else:
                data[len(data)-1] = M201_limit_old + "\n" + M205_jerk_old + "\n" + data[len(data)-1]
            return data
        
        
        elif not constant_change:
            layer_spread = end_index - start_index
            x_accel_hyst = round((accel_old - int(x_accel)) / layer_spread)
            y_accel_hyst = round((accel_old - int(y_accel)) / layer_spread)
            x_accel_start = round(round((accel_old - x_accel_hyst)/50)*50)
            y_accel_start = round(round((accel_old - y_accel_hyst)/50)*50)
            M201_limit_new = "M201 X" + str(x_accel_start) + " Y" + str(y_accel_start)
            #Add Accel limit and new Jerk at start layer-------------------------------------------------------------
            layer = data[start_index]
            lines = layer.split("\n")
            for index, line in enumerate(lines):
                if lines[index].startswith(";LAYER:"):
                    lines.insert(index+1,M201_limit_new)
                    if self.getSettingValueByKey("jerk_enable"):
                        lines.insert(index+2,M205_jerk_new)
                    data[start_index] = "\n".join(lines)
                    break
            for num in range(start_index + 1, end_index,1):
                layer = data[num]
                lines = layer.split("\n")
                x_accel_start -= x_accel_hyst
                if x_accel_start < int(x_accel): x_accel_start = int(x_accel)
                y_accel_start -= y_accel_hyst
                if y_accel_start < int(y_accel): y_accel_start = int(y_accel)
                M201_limit_new = "M201 X" + str(round(round(x_accel_start/50)*50)) + " Y" + str(round(round(y_accel_start/50)*50))
                for index, line in enumerate(lines):
                    if line.startswith(";LAYER:"):
                        lines.insert(index+1, M201_limit_new)
                        continue
                data[num] = "\n".join(lines)
            #Alter any existing jerk lines.  Accel lines can be ignored-----------------------------------       
            if self.getSettingValueByKey("jerk_enable"):
                for num in range(start_index,len(data)-1,1):
                    layer = data[num]
                    lines = layer.split("\n")
                    for index, line in enumerate(lines):
                        if line.startswith("M205"):
                            lines[index] = re.sub(M205_jerk_pattern, M205_jerk_new, line)
                    data[num] = "\n".join(lines)
                data[len(data)-1] = M201_limit_old + "\n" + M205_jerk_old + "\n" + data[len(data)-1]
            return data