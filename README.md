# VPN-Profile-Manager

## Usage
- Launch **VPN Profile Manager** (from `VPNProfileManager.exe` in the PyInstaller `dist` folder or from the installed Start Menu shortcut).
- Add or import profiles, then select one and click **Connect**.
- For OpenConnect profiles you can optionally set an auth group; for OpenVPN profiles you must attach the `.ovpn` file so it can be passed to the client.
- Connection output and errors stream into the **Logs** panel so you can verify what the CLI clients are doing.

## Credential setup
- Usernames are stored with each profile. Passwords are saved to the system keyring the first time you enter them in the connect dialog or profile editor; they are recalled automatically on the next connection attempt.
- Removing a profile clears its stored credentials. To force a new prompt, delete the profile or remove the matching entry from your OS keyring.

## VPN client executables
- The app automatically searches for `openconnect.exe` and `openvpn.exe` in the following order:
  1. Environment overrides: `VPNPM_OPENCONNECT_PATH` and `VPNPM_OPENVPN_PATH`.
  2. A `bin` directory next to the running executable (used by the packaged build).
  3. `%ProgramFiles%\VPNProfileManager\bin` (installed layout) and the standard OpenConnect/OpenVPN install paths.
  4. Anything already on `PATH`.
- When building/packaging, place the desired client binaries in `vendor/windows`. They will be copied into `bin` so the Inno Setup installer deploys them under `Program Files\VPNProfileManager\bin`.

## Building and installing
### Prerequisites
- Python 3.11+ on Windows with `pip install pyinstaller PySide6 keyring` (match versions to your Python environment).
- Copy the desired VPN client binaries into `vendor/windows/openconnect.exe` and `vendor/windows/openvpn.exe`.

### PyInstaller one-folder build
1. From the repository root (required so the spec can resolve paths), run:
   ```bash
   python -m PyInstaller packaging/pyinstaller-onefolder.spec
   ```
2. The distributable lands in `dist/VPNProfileManager/` with a `bin` folder containing the bundled VPN clients.

### Inno Setup installer
1. Open `installer/VPNProfileManager.iss` in Inno Setup (or run `ISCC installer/VPNProfileManager.iss`).
2. Ensure `dist/VPNProfileManager/` is present from the previous step; the script recurses that folder and installs everything into `C:\\Program Files\\VPNProfileManager`, including `bin`.
3. Run the generated `VPNProfileManagerSetup.exe` to install. After installation, launch **VPN Profile Manager** from the Start Menu or desktop shortcut.
