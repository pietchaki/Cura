// Copyright (c) 2022 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Window 2.1

import UM 1.3 as UM
import Cura 1.0 as Cura

UM.Dialog
{
    // This dialog asks the user whether he/she wants to open the project file we have detected or the model files.
    id: base

    title: catalog.i18nc("@title:window", "Open file(s)")
    width: 420 * screenScaleFactor
    height: 170 * screenScaleFactor

    maximumHeight: height
    maximumWidth: width
    minimumHeight: height
    minimumWidth: width

    modality: Qt.WindowModal

    property var fileUrls: []
    property var addToRecent: true
    property int spacerHeight: 10 * screenScaleFactor

    function loadProjectFile(projectFile)
    {
        UM.WorkspaceFileHandler.readLocalFile(projectFile, base.addToRecent);
    }

    function loadModelFiles(fileUrls)
    {
        for (var i in fileUrls)
        {
            CuraApplication.readLocalFile(fileUrls[i], "open_as_model", base.addToRecent);
        }
    }

    Column
    {
        anchors.fill: parent
        anchors.leftMargin: 20 * screenScaleFactor
        anchors.rightMargin: 20 * screenScaleFactor
        anchors.bottomMargin: 20 * screenScaleFactor
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 10 * screenScaleFactor

        Label
        {
            text: catalog.i18nc("@text:window", "We have found one or more project file(s) within the files you have selected. You can open only one project file at a time. We suggest to only import models from those files. Would you like to proceed?")
            anchors.left: parent.left
            anchors.right: parent.right
            font: UM.Theme.getFont("default")
            wrapMode: Text.WordWrap
        }

        Item // Spacer
        {
            height: base.spacerHeight
            width: height
        }

        UM.I18nCatalog
        {
            id: catalog
            name: "cura"
        }

        ButtonGroup {
            buttons: [cancelButton, importAllAsModelsButton]
            checkedButton: importAllAsModelsButton
        }
    }

    onAccepted: loadModelFiles(base.fileUrls)

    // Buttons
    rightButtons:
    [
        Button
        {
            id: cancelButton
            text: catalog.i18nc("@action:button", "Cancel");
            onClicked:
            {
                // cancel
                base.hide();
            }
        },
        Button
        {
            id: importAllAsModelsButton
            text: catalog.i18nc("@action:button", "Import all as models");
            onClicked:
            {
                // load models from all selected file
                loadModelFiles(base.fileUrls);
                base.hide();
            }
        }
    ]
}