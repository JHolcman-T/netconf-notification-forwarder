from netconf_notification_forwarder.app_entrypoint import start
import netconf_notification_forwarder.cli as cli

if __name__ == "__main__":
    arguments = cli.get_arguments()
    start(
        ip_address=arguments.ip_address,
        port=arguments.port,
        logging_style=arguments.log_style,
        logging_level=arguments.log_level,
        settings_file_path=arguments.config_file,
        host_key=arguments.host_key,
    )
