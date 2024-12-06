import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

class UnattendCreator:
    def __init__(self):
        self.settings = {
            # System Settings
            'computer_name': 'PC-NAME',
            'organization': 'Organization',
            'owner': 'Owner',
            'product_key': '',
            
            # Regional Settings
            'timezone': 'UTC',
            'language': 'en-US',
            'input_locale': 'en-US',
            'system_locale': 'en-US',
            'user_locale': 'en-US',
            'keyboard_layout': '0409:00000409',  # US keyboard
            
            # Network Settings
            'network_location': 'Work',  # Home, Work, or Public
            'disable_ipv6': False,
            'disable_netbios': False,
            'disable_firewall': False,
            
            # User Account Settings
            'user_account': '',
            'user_password': '',
            'user_account_type': 'Administrator',  # Administrator or Standard
            'auto_logon': False,
            'auto_logon_count': 1,
            'admin_password': '',
            'disable_admin_account': False,
            'enable_guest_account': False,
            
            # Windows Settings
            'windows_edition': 'Windows 10 Pro',
            'install_updates': True,
            'install_drivers': True,
            'enable_remote_desktop': False,
            'enable_remote_assistance': False,
            
            # Privacy Settings
            'disable_telemetry': True,
            'disable_cortana': True,
            'disable_consumer_features': True,
            'disable_windows_tips': True,
            'disable_app_suggestions': True,
            'disable_feedback': True,
            
            # UI Settings
            'skip_eula': True,
            'skip_express': True,
            'hide_wireless': True,
            'dark_theme': False,
            'small_taskbar': False,
            'show_file_extensions': True,
            'show_hidden_files': False,
            
            # Power Settings
            'power_plan': 'Balanced',  # Balanced, High Performance, Power Saver
            'sleep_timeout_ac': 30,  # minutes, 0 for never
            'sleep_timeout_dc': 15,
            'hibernate_timeout_ac': 0,
            'hibernate_timeout_dc': 0,
            
            # Security Settings
            'bitlocker_encryption': False,
            'secure_boot': True,
            'tpm_enabled': True,
            'password_complexity': True,
            'password_expiration': False,
            'password_history': 0,
            
            # App Settings
            'remove_inbox_apps': True,
            'install_winget': True,
            'install_chocolatey': False,
            'install_office': False,
            'office_edition': 'Professional Plus 2021'
        }

    @staticmethod
    def get_available_timezones():
        return [
            'UTC', 'GMT Standard Time', 'Pacific Standard Time',
            'Mountain Standard Time', 'Central Standard Time',
            'Eastern Standard Time', 'Romance Standard Time',
            'Central Europe Standard Time', 'India Standard Time',
            'China Standard Time', 'Tokyo Standard Time',
            'AUS Eastern Standard Time', 'New Zealand Standard Time',
            'GMT+01:00', 'GMT+02:00', 'GMT+03:00', 'GMT+04:00',
            'GMT+05:00', 'GMT+06:00', 'GMT+07:00', 'GMT+08:00',
            'GMT+09:00', 'GMT+10:00', 'GMT+11:00', 'GMT+12:00',
            'GMT-01:00', 'GMT-02:00', 'GMT-03:00', 'GMT-04:00',
            'GMT-05:00', 'GMT-06:00', 'GMT-07:00', 'GMT-08:00',
            'GMT-09:00', 'GMT-10:00', 'GMT-11:00', 'GMT-12:00'
        ]

    @staticmethod
    def get_available_languages():
        return {
            'en-US': 'English (United States)',
            'en-GB': 'English (United Kingdom)',
            'es-ES': 'Spanish (Spain)',
            'fr-FR': 'French (France)',
            'de-DE': 'German (Germany)',
            'it-IT': 'Italian (Italy)',
            'pt-PT': 'Portuguese (Portugal)',
            'ru-RU': 'Russian (Russia)',
            'ja-JP': 'Japanese (Japan)',
            'ko-KR': 'Korean (Korea)',
            'zh-CN': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)',
            'ar-SA': 'Arabic (Saudi Arabia)',
            'hi-IN': 'Hindi (India)',
            'th-TH': 'Thai (Thailand)',
            'tr-TR': 'Turkish (Turkey)',
            'nl-NL': 'Dutch (Netherlands)',
            'pl-PL': 'Polish (Poland)',
            'vi-VN': 'Vietnamese (Vietnam)'
        }

    @staticmethod
    def get_keyboard_layouts():
        return {
            '0409:00000409': 'US',
            '0809:00000809': 'UK',
            '0c0c:0000040c': 'French',
            '0407:00000407': 'German',
            '0410:00000410': 'Italian',
            '0419:00000419': 'Russian',
            '0411:00000411': 'Japanese',
            '0412:00000412': 'Korean',
            '0804:00000804': 'Chinese (Simplified)',
            '0404:00000404': 'Chinese (Traditional)'
        }

    @staticmethod
    def get_windows_editions():
        return [
            'Windows 10 Home',
            'Windows 10 Pro',
            'Windows 10 Pro for Workstations',
            'Windows 10 Enterprise',
            'Windows 10 Education',
            'Windows 11 Home',
            'Windows 11 Pro',
            'Windows 11 Pro for Workstations',
            'Windows 11 Enterprise',
            'Windows 11 Education'
        ]

    @staticmethod
    def get_office_editions():
        return [
            'Professional Plus 2021',
            'Standard 2021',
            'Professional Plus 2019',
            'Standard 2019',
            'Microsoft 365 Apps for Enterprise',
            'Microsoft 365 Apps for Business'
        ]

    def create_unattend_xml(self):
        # Create root element
        root = ET.Element('unattend', xmlns="urn:schemas-microsoft-com:unattend")
        
        # Settings for Windows PE (Pre-Installation)
        self._add_settings_pass(root, 'windowsPE', 1)
        
        # Settings for OOBE (Out-of-Box Experience)
        self._add_settings_pass(root, 'oobeSystem', 7)
        
        # Settings for specialize pass
        self._add_settings_pass(root, 'specialize', 6)

        # Create the XML string with proper formatting
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        return xml_str

    def _add_settings_pass(self, root, pass_name, pass_number):
        settings_pass = ET.SubElement(root, 'settings', {'pass': pass_name})
        
        # Add components based on settings
        self._add_shell_setup(settings_pass, pass_name)
        self._add_international_core(settings_pass)
        self._add_network_settings(settings_pass)
        self._add_security_settings(settings_pass)
        self._add_power_settings(settings_pass)
        
        if pass_name == 'specialize':
            self._add_system_settings(settings_pass)

    def _add_shell_setup(self, parent, pass_name):
        component = self._create_component(parent, 'Microsoft-Windows-Shell-Setup')
        
        if pass_name == 'windowsPE':
            self._add_computer_name(component)
        elif pass_name == 'oobeSystem':
            self._add_user_accounts(component)
            self._add_auto_logon(component)
            self._add_oobe_settings(component)
        elif pass_name == 'specialize':
            self._add_registered_organization(component)
            self._add_registered_owner(component)
            self._add_time_zone(component)

    def _create_component(self, parent, name):
        return ET.SubElement(parent, 'component', {
            'name': name,
            'processorArchitecture': 'amd64',
            'publicKeyToken': '31bf3856ad364e35',
            'language': 'neutral',
            'versionScope': 'nonSxS'
        })

    def _add_computer_name(self, component):
        computer_name = ET.SubElement(component, 'ComputerName')
        computer_name.text = self.settings['computer_name']

    def _add_user_accounts(self, component):
        user_accounts = ET.SubElement(component, 'UserAccounts')
        local_accounts = ET.SubElement(user_accounts, 'LocalAccounts')
        local_account = ET.SubElement(local_accounts, 'LocalAccount')
        
        description = ET.SubElement(local_account, 'Description')
        description.text = f"Account for {self.settings['user_account']}"
        
        display_name = ET.SubElement(local_account, 'DisplayName')
        display_name.text = self.settings['user_account']
        
        group = ET.SubElement(local_account, 'Group')
        group.text = 'Administrators' if self.settings['user_account_type'] == 'Administrator' else 'Users'
        
        name = ET.SubElement(local_account, 'Name')
        name.text = self.settings['user_account']
        
        if self.settings['user_password']:
            password = ET.SubElement(local_account, 'Password')
            value = ET.SubElement(password, 'Value')
            value.text = self.settings['user_password']
            plain_text = ET.SubElement(password, 'PlainText')
            plain_text.text = 'true'

    def _add_auto_logon(self, component):
        if self.settings['auto_logon']:
            auto_logon = ET.SubElement(component, 'AutoLogon')
            password = ET.SubElement(auto_logon, 'Password')
            value = ET.SubElement(password, 'Value')
            value.text = self.settings['user_password']
            plain_text = ET.SubElement(password, 'PlainText')
            plain_text.text = 'true'
            username = ET.SubElement(auto_logon, 'Username')
            username.text = self.settings['user_account']
            enabled = ET.SubElement(auto_logon, 'Enabled')
            enabled.text = 'true'
            logon_count = ET.SubElement(auto_logon, 'LogonCount')
            logon_count.text = str(self.settings['auto_logon_count'])

    def _add_oobe_settings(self, component):
        oobe = ET.SubElement(component, 'OOBE')
        
        if self.settings['skip_eula']:
            hide_eula = ET.SubElement(oobe, 'HideEULAPage')
            hide_eula.text = 'true'
        
        if self.settings['skip_express']:
            protect_your_pc = ET.SubElement(oobe, 'ProtectYourPC')
            protect_your_pc.text = '1'
        
        if self.settings['hide_wireless']:
            hide_wireless = ET.SubElement(oobe, 'HideWirelessSetupInOOBE')
            hide_wireless.text = 'true'

    def _add_registered_organization(self, component):
        if self.settings['organization']:
            org_name = ET.SubElement(component, 'RegisteredOrganization')
            org_name.text = self.settings['organization']

    def _add_registered_owner(self, component):
        if self.settings['owner']:
            owner_name = ET.SubElement(component, 'RegisteredOwner')
            owner_name.text = self.settings['owner']

    def _add_time_zone(self, component):
        time_zone = ET.SubElement(component, 'TimeZone')
        time_zone.text = self.settings['timezone']

    def _add_international_core(self, parent):
        component = self._create_component(parent, 'Microsoft-Windows-International-Core')
        
        input_locale = ET.SubElement(component, 'InputLocale')
        input_locale.text = self.settings['input_locale']
        
        system_locale = ET.SubElement(component, 'SystemLocale')
        system_locale.text = self.settings['system_locale']
        
        user_locale = ET.SubElement(component, 'UserLocale')
        user_locale.text = self.settings['user_locale']
        
        keyboard_layout = ET.SubElement(component, 'UILanguage')
        keyboard_layout.text = self.settings['language']

    def _add_network_settings(self, parent):
        component = self._create_component(parent, 'Microsoft-Windows-TCPIP')
        
        if self.settings['disable_ipv6']:
            ipv6 = ET.SubElement(component, 'IPv6')
            ipv6.text = 'false'
        
        if self.settings['disable_netbios']:
            netbios = ET.SubElement(component, 'NetbiosOptions')
            netbios.text = '2'
        
        if self.settings['disable_firewall']:
            firewall = ET.SubElement(component, 'Firewall')
            firewall.text = 'false'

    def _add_security_settings(self, parent):
        component = self._create_component(parent, 'Microsoft-Windows-Security-SPP-UX-Clien')
        
        if self.settings['bitlocker_encryption']:
            bitlocker = ET.SubElement(component, 'BitLocker')
            bitlocker.text = 'true'
        
        if self.settings['secure_boot']:
            secure_boot = ET.SubElement(component, 'SecureBoot')
            secure_boot.text = 'true'
        
        if self.settings['tpm_enabled']:
            tpm = ET.SubElement(component, 'TPM')
            tpm.text = 'true'
        
        if self.settings['password_complexity']:
            password_complexity = ET.SubElement(component, 'PasswordComplexity')
            password_complexity.text = 'true'
        
        if self.settings['password_expiration']:
            password_expiration = ET.SubElement(component, 'PasswordExpiration')
            password_expiration.text = 'true'
        
        if self.settings['password_history']:
            password_history = ET.SubElement(component, 'PasswordHistory')
            password_history.text = str(self.settings['password_history'])

    def _add_power_settings(self, parent):
        component = self._create_component(parent, 'Microsoft-Windows-powermgmt')
        
        power_plan = ET.SubElement(component, 'PowerPlan')
        power_plan.text = self.settings['power_plan']
        
        sleep_timeout_ac = ET.SubElement(component, 'SleepTimeoutAC')
        sleep_timeout_ac.text = str(self.settings['sleep_timeout_ac'])
        
        sleep_timeout_dc = ET.SubElement(component, 'SleepTimeoutDC')
        sleep_timeout_dc.text = str(self.settings['sleep_timeout_dc'])
        
        hibernate_timeout_ac = ET.SubElement(component, 'HibernateTimeoutAC')
        hibernate_timeout_ac.text = str(self.settings['hibernate_timeout_ac'])
        
        hibernate_timeout_dc = ET.SubElement(component, 'HibernateTimeoutDC')
        hibernate_timeout_dc.text = str(self.settings['hibernate_timeout_dc'])

    def _add_system_settings(self, parent):
        component = self._create_component(parent, 'Microsoft-Windows-System')
        
        if self.settings['remove_inbox_apps']:
            remove_inbox_apps = ET.SubElement(component, 'RemoveInboxApps')
            remove_inbox_apps.text = 'true'
        
        if self.settings['install_winget']:
            install_winget = ET.SubElement(component, 'InstallWinget')
            install_winget.text = 'true'
        
        if self.settings['install_chocolatey']:
            install_chocolatey = ET.SubElement(component, 'InstallChocolatey')
            install_chocolatey.text = 'true'
        
        if self.settings['install_office']:
            install_office = ET.SubElement(component, 'InstallOffice')
            install_office.text = 'true'
            office_edition = ET.SubElement(component, 'OfficeEdition')
            office_edition.text = self.settings['office_edition']

    def save_unattend_file(self, file_path):
        try:
            xml_content = self.create_unattend_xml()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            return True, "Unattend file created successfully"
        except Exception as e:
            return False, f"Error creating unattend file: {str(e)}"
