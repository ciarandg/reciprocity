{
  self,
  config,
  lib,
  pkgs,
  ...
}: let
  cfg = config.services.reciprocity;
in {
  options.services.reciprocity = {
    enable = lib.mkEnableOption "reciprocity recipe OCR daemon";

    config = lib.mkOption {
      type = lib.types.nullOr lib.types.attrs;
      default = null;
      description = "The content of config.json";
    };

    package = lib.mkOption {
      type = lib.types.package;
      default = self.outputs.packages.${pkgs.system}.reciprocity;
      description = "Package providing the reciprocity executable.";
    };

    user = lib.mkOption {
      type = lib.types.str;
      default = "reciprocity";
      description = "User to run the reciprocity daemon as.";
    };

    group = lib.mkOption {
      type = lib.types.str;
      default = "reciprocity";
      description = "Group to run the reciprocity daemon as.";
    };
  };

  config = lib.mkIf cfg.enable {
    users.groups.${cfg.group} = {};

    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
    };

    systemd.services.reciprocity = let
      configFile =
        if cfg.config == null
        then null
        else builtins.toFile "reciprocity-config.json" (builtins.toJSON cfg.config);
    in {
      description = "A daemon for converting recipe scans to Markdown";
      wantedBy = ["multi-user.target"];
      after = ["network.target"];

      path = [
        pkgs.poppler-utils
        pkgs.tesseract
      ];

      serviceConfig = {
        ExecStartPre = "${lib.getExe cfg.package} setup";
        ExecStart = "${lib.getExe cfg.package} watch -i ./in -o ./out";

        Environment = lib.optionals (configFile != null) [
          "RECIPROCITY_CONFIG_FILE=${configFile}"
        ];

        Restart = "on-failure";
        RestartSec = 5;

        User = cfg.user;
        Group = cfg.group;

        StateDirectory = "reciprocity";
        WorkingDirectory = "%S/reciprocity";

        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectControlGroups = true;
        RestrictSUIDSGID = true;
        LockPersonality = true;
        MemoryDenyWriteExecute = true;
      };
    };
  };
}
