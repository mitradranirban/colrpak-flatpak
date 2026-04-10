# ColrPak FlatPak
## Flatpak repository for ColrPak
! [Screenshot](https://github.com/mitradranirban/colr-pak/screenshot.png)

### Installation 
* If Flatpak is already not enabled in your Linux distro, follow [these instructions](https://flatpak.org/setup/) for you distribution to enable it.
* If Flatpak is integrated with your Software Centre (as in Fedora Workstation, Monjaro), just download [this file](https://mitradranirban.github.io/colrpak-flatpak/in.atipra.ColrPak.flatpakref) , then right click it, and select "Open with -> Software Install" .
* Otherwise, copy and paste the following command in your terminal

```
flatpak install --from https://mitradranirban.github.io/colrpak-flatpak/in atipra.ColrPak.flatpakref
```
* Type Y for yes and provide your password when prompted
* Fontrapak with all its dependancy will be installed in your computer

### Updating ColrPak Flatpak
* If ColrPak is showing in your Software centre, you can press the "Update" button to update to the latest version.
* Otherwise. open your terminal and type
```
flatpak update in.atipra.ColrPak
```
### Running ColrPak Flatpak
* In terminal, start the application by typing
```
flatpak run in.atipra.ColrPak
```
* Alternatively, open your app menu app menu and click on the Fontra icon
* 
  ![ColrPak icon](data/icons/in.atipra.ColrPak.svg)
  
### Report Issues 
 
For any  problem in using the flatpak, please [open an Issue](https://github.com/mitradranirban/colr-pak/issues)
