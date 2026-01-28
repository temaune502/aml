AML Test Build
==============

This folder contains everything needed to run and compile AML programs.

Structure:
- aml/ : Core interpreter engine
- plugins/ : Python plugins for automation, system, etc.
- sdk/ & temaune/ : Standard AML library modules
- aml.py : The main runner
- aml_compiler.py : The CAML compiler
- aml_runtime_access.py : Bridge for Python plugins

How to run:
1. Open terminal in this folder.
2. Run: python aml.py <your_file.aml_or_caml>

Example:
Run 'run_demo.bat' to see the reactive demo in action (using reactive_demo.caml).

How to compile:
python aml_compiler.py your_script.aml your_app.caml
