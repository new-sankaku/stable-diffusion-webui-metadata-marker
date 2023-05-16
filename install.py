import launch

# TODO: add pip dependency if need extra module only on extension

# if not launch.is_installed("aitextgen"):
#     launch.run_pip("install aitextgen==0.6.0", "requirements for MagicPrompt")

if not launch.is_installed("pypng"):
    launch.run_pip("install pypng", "requirements for metadata preservation")

if not launch.is_installed("numpy"):
    launch.run_pip("install numpy", "requirements for metadata preservation")

if not launch.is_installed("matplotlib"):
    launch.run_pip("install matplotlib", "requirements for metadata preservation")
    
if not launch.is_installed("pillow"):
    launch.run_pip("install pillow", "requirements for metadata preservation")
