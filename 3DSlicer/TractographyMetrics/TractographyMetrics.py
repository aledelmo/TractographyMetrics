#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

import ctk
import qt
import slicer

__author__ = 'Alessandro Delmonte'
__email__ = 'delmonte.ale92@gmail.com'


class TractographyMetrics:
    def __init__(self, parent):
        parent.title = 'Tractography Metrics'
        parent.categories = ['IMAG2', 'Diffusion Pelvis']
        parent.dependencies = []
        parent.contributors = ['Alessandro Delmonte (IMAG2)']
        parent.helpText = '''INSERT HELP TEXT.'''
        parent.acknowledgementText = '''Module developed for 3DSlicer (<a>http://www.slicer.org</a>)'''

        self.parent = parent

        module_dir = os.path.dirname(self.parent.path)
        icon_path = os.path.join(module_dir, 'Resources', 'icon.png')
        if os.path.isfile(icon_path):
            parent.icon = qt.QIcon(icon_path)

        try:
            slicer.selfTests
        except AttributeError:
            slicer.selfTests = {}
        slicer.selfTests['PQL'] = self.runTest

    def __repr__(self):
        return 'TractographyMetrics(parent={})'.format(self.parent)

    def __str__(self):
        return 'TractographyMetrics module initialization class.'

    @staticmethod
    def runTest():
        tester = TractographyMetricsTest()
        tester.runTest()


# class It:
#     def __init__(self, node): self.node = node
#
#     def __enter__(self): return self.node
#
#     def __exit__(self, type, value, traceback): return False


class TractographyMetricsWidget:
    def __init__(self, parent=None):
        self.moduleName = self.__class__.__name__
        if self.moduleName.endswith('Widget'):
            self.moduleName = self.moduleName[:-6]
        settings = qt.QSettings()
        try:
            self.developerMode = settings.value('Developer/DeveloperMode').lower() == 'true'
        except AttributeError:
            self.developerMode = settings.value('Developer/DeveloperMode') is True

        self.tmp = tempfile.mkdtemp()
        self.logic = TractographyMetricsLogic(self.tmp)

        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()

        if not parent:
            self.setup()
            self.parent.show()

    def __repr__(self):
        return 'TractographyMetricsWidget(parent={})'.format(self.parent)

    def __str__(self):
        return 'TractographyMetrics GUI class'

    def setup(self):
        tm_collapsible_button = ctk.ctkCollapsibleButton()
        tm_collapsible_button.text = 'Fiber Bundle Evaluation'

        self.layout.addWidget(tm_collapsible_button)

        tm_form_layout = qt.QFormLayout(tm_collapsible_button)
        tm_form_layout.setVerticalSpacing(13)

        self.tracto_node_selector = slicer.qMRMLNodeComboBox()
        self.tracto_node_selector.nodeTypes = ['vtkMRMLFiberBundleNode']
        self.tracto_node_selector.selectNodeUponCreation = True
        self.tracto_node_selector.addEnabled = False
        self.tracto_node_selector.removeEnabled = False
        self.tracto_node_selector.noneEnabled = False
        self.tracto_node_selector.showHidden = False
        self.tracto_node_selector.renameEnabled = False
        self.tracto_node_selector.showChildNodeTypes = False
        self.tracto_node_selector.setMRMLScene(slicer.mrmlScene)

        self.tracto_node_selector.connect('nodeActivated(vtkMRMLNode*)', self.on_tracto_node_select)

        self.tracto_node = self.tracto_node_selector.currentNode()

        tm_form_layout.addRow('Input Fiber Bundle: ', self.tracto_node_selector)

        self.output_file_selector = ctk.ctkPathLineEdit()
        self.output_file_selector.filters = ctk.ctkPathLineEdit.Files | ctk.ctkPathLineEdit.Writable | \
                                            ctk.ctkPathLineEdit.Hidden
        self.output_file_selector.addCurrentPathToHistory()
        tm_form_layout.addRow("Output File: ", self.output_file_selector)

        line = qt.QFrame()
        line.setFrameShape(qt.QFrame().HLine)
        line.setFrameShadow(qt.QFrame().Sunken)
        tm_form_layout.addRow(line)

        groupbox = qt.QGroupBox()
        groupbox.setTitle('Optional scalar map measurements:')
        options_grid_layout = qt.QGridLayout(groupbox)
        options_grid_layout.setColumnStretch(1, 1)
        options_grid_layout.setColumnStretch(2, 1)
        options_grid_layout.setColumnStretch(3, 1)

        self.bzero_selector = slicer.qMRMLNodeComboBox()
        self.bzero_selector.nodeTypes = ['vtkMRMLScalarVolumeNode']
        self.bzero_selector.selectNodeUponCreation = True
        self.bzero_selector.addEnabled = False
        self.bzero_selector.removeEnabled = False
        self.bzero_selector.noneEnabled = True
        self.bzero_selector.showHidden = False
        self.bzero_selector.renameEnabled = False
        self.bzero_selector.showChildNodeTypes = False
        self.bzero_selector.setMRMLScene(slicer.mrmlScene)

        self.bzero_selector.connect('nodeActivated(vtkMRMLNode*)', self.on_bzero_select)

        self.bzero_node = self.bzero_selector.currentNode()

        self.fa_selector = slicer.qMRMLNodeComboBox()
        self.fa_selector.nodeTypes = ['vtkMRMLScalarVolumeNode']
        self.fa_selector.selectNodeUponCreation = True
        self.fa_selector.addEnabled = False
        self.fa_selector.removeEnabled = False
        self.fa_selector.noneEnabled = True
        self.fa_selector.showHidden = False
        self.fa_selector.renameEnabled = False
        self.fa_selector.showChildNodeTypes = False
        self.fa_selector.setMRMLScene(slicer.mrmlScene)

        self.fa_selector.connect('nodeActivated(vtkMRMLNode*)', self.on_fa_select)

        self.fa_node = self.fa_selector.currentNode()

        self.md_selector = slicer.qMRMLNodeComboBox()
        self.md_selector.nodeTypes = ['vtkMRMLScalarVolumeNode']
        self.md_selector.selectNodeUponCreation = True
        self.md_selector.addEnabled = False
        self.md_selector.removeEnabled = False
        self.md_selector.noneEnabled = True
        self.md_selector.showHidden = False
        self.md_selector.renameEnabled = False
        self.md_selector.showChildNodeTypes = False
        self.md_selector.setMRMLScene(slicer.mrmlScene)

        self.md_selector.connect('nodeActivated(vtkMRMLNode*)', self.on_md_select)

        self.md_node = self.md_selector.currentNode()

        bzero_textwidget = qt.QLabel()
        bzero_textwidget.setText('b-zero: ')
        fa_textwidget = qt.QLabel()
        fa_textwidget.setText('FA: ')
        md_textwidget = qt.QLabel()
        md_textwidget.setText('MD: ')

        options_grid_layout.addWidget(bzero_textwidget, 0, 0, 1, 1)
        options_grid_layout.addWidget(self.bzero_selector, 0, 1, 1, 4)
        options_grid_layout.addWidget(fa_textwidget, 1, 0, 1, 1)
        options_grid_layout.addWidget(self.fa_selector, 1, 1, 1, 4)
        options_grid_layout.addWidget(md_textwidget, 2, 0, 1, 1)
        options_grid_layout.addWidget(self.md_selector, 2, 1, 1, 4)

        tm_form_layout.addRow(groupbox)

        self.to_plot = qt.QCheckBox('')
        self.to_plot.setChecked(True)

        tm_form_layout.addRow('Plot distribution:', self.to_plot)

        line2 = qt.QFrame()
        line2.setFrameShape(qt.QFrame().HLine)
        line2.setFrameShadow(qt.QFrame().Sunken)
        tm_form_layout.addRow(line2)

        save_grid_layout = qt.QGridLayout()
        save_grid_layout.setColumnStretch(0, 0)
        save_grid_layout.setColumnStretch(0, 0)

        self.to_csv = qt.QCheckBox('CSV')
        self.to_csv.setChecked(False)
        self.to_xlsx = qt.QCheckBox('xlsx')
        self.to_xlsx.setChecked(False)

        save_grid_layout.addWidget(self.to_csv, 0, 0)
        save_grid_layout.addWidget(self.to_xlsx, 0, 1)

        tm_form_layout.addRow('Save additional files:', save_grid_layout)

        self.additional_info = qt.QPlainTextEdit()
        self.additional_info.setPlainText('')

        n = 5
        m = qt.QFontMetrics(self.additional_info.font)
        self.additional_info.setFixedHeight((n + 1) * int(m.lineSpacing()))
        tm_form_layout.addRow('Supplementary info:', self.additional_info)

        self.compute_button = qt.QPushButton('Compute')
        self.compute_button.enabled = True

        self.compute_button.connect('clicked(bool)', self.on_compute_button)
        tm_form_layout.addRow(self.compute_button)

        self.layout.addStretch(1)

        if self.developerMode:

            def createHLayout(elements):
                widget = qt.QWidget()
                rowLayout = qt.QHBoxLayout()
                widget.setLayout(rowLayout)
                for element in elements:
                    rowLayout.addWidget(element)
                return widget

            """Developer interface"""
            self.reloadCollapsibleButton = ctk.ctkCollapsibleButton()
            self.reloadCollapsibleButton.text = "Reload && Test"
            self.layout.addWidget(self.reloadCollapsibleButton)
            reloadFormLayout = qt.QFormLayout(self.reloadCollapsibleButton)

            self.reloadButton = qt.QPushButton("Reload")
            self.reloadButton.toolTip = "Reload this module."
            self.reloadButton.name = "ScriptedLoadableModuleTemplate Reload"
            self.reloadButton.connect('clicked()', self.onReload)

            self.reloadAndTestButton = qt.QPushButton("Reload and Test")
            self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
            self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

            self.editSourceButton = qt.QPushButton("Edit")
            self.editSourceButton.toolTip = "Edit the module's source code."
            self.editSourceButton.connect('clicked()', self.onEditSource)

            self.restartButton = qt.QPushButton("Restart Slicer")
            self.restartButton.toolTip = "Restart Slicer"
            self.restartButton.name = "ScriptedLoadableModuleTemplate Restart"
            self.restartButton.connect('clicked()', slicer.app.restart)

            reloadFormLayout.addWidget(
                createHLayout([self.reloadButton, self.reloadAndTestButton, self.editSourceButton, self.restartButton]))

    def on_tracto_node_select(self):
        self.tracto_node = self.tracto_node_selector.currentNode()

    def on_bzero_select(self):
        self.bzero_node = self.bzero_selector.currentNode()

    def on_fa_select(self):
        self.fa_node = self.fa_selector.currentNode()

    def on_md_select(self):
        self.md_node = self.md_selector.currentNode()

    def on_compute_button(self):
        self.output_file_selector.addCurrentPathToHistory()
        print(self.output_file_selector.currentPath)
        print(self.additional_info.document().toPlainText().encode('utf8'))

    def onReload(self):

        print('\n' * 2)
        print('-' * 30)
        print('Reloading module: ' + self.moduleName)
        print('-' * 30)
        print('\n' * 2)

        slicer.util.reloadScriptedModule(self.moduleName)

    def onReloadAndTest(self):
        try:
            self.onReload()
            test = slicer.selfTests[self.moduleName]
            test()
        except Exception:
            import traceback
            traceback.print_exc()
            errorMessage = "Reload and Test: Exception!\n\n" + "See Python Console for Stack Trace"
            slicer.util.errorDisplay(errorMessage)

    def onEditSource(self):
        filePath = slicer.util.modulePath(self.moduleName)
        qt.QDesktopServices.openUrl(qt.QUrl("file:///" + filePath, qt.QUrl.TolerantMode))

    def cleanup(self):
        for filename in os.listdir(self.tmp):
            path = os.path.join(self.tmp, filename)
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


class TractographyMetricsLogic:
    def __init__(self, temp_folder):
        self.temp_folder = temp_folder


class TractographyMetricsTest(unittest.TestCase):

    def __init__(self):
        super(TractographyMetricsTest, self).__init__()

    def __repr__(self):
        return 'TractographyMetrics(). Derived from {}'.format(unittest.TestCase)

    def __str__(self):
        return 'TractographyMetrics test class'

    def runTest(self, scenario=None):
        pass
