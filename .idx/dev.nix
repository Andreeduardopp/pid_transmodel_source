{ pkgs, ... }: {
  # Qual canal do Nixpkgs usar.
  channel = "stable-23.11"; # ou "unstable"

  # Pacotes a serem instalados no ambiente.
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.docker-compose
    # Postgres e Redis podem ser instalados como pacotes ou serviços.
    # Aqui instalamos os clientes/ferramentas.
    pkgs.postgresql_15 
    pkgs.redis
  ];

  # Variáveis de ambiente
  env = {
    # Evita criar __pycache__ em todo lugar
    PYTHONDONTWRITEBYTECODE = "1";
    PYTHONUNBUFFERED = "1";
  };

  # Configuração de serviços.
  idx = {
    extensions = [
      "ms-python.python"
      "batisteo.vscode-django"
      "mtxr.sqltools"
      "charliermarsh.ruff"
    ];

    # Habilita suporte a Docker
    workspace = {
      onCreate = {
        # Executa setup na criação
        setup = "bash ./setup_projeto.sh";
      };
      onStart = {
        # Garante que os serviços docker subam se houver docker-compose, 
        # mas aqui focaremos em rodar os comandos de preview.
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          # Monolito Django
          command = ["python" "monolito/manage.py" "runserver" "0.0.0.0:8000"];
          manager = "web";
          env = {
            PORT = "8000";
          };
        };
        bot-whatsapp = {
          # Interface FastAPI
          command = ["uvicorn" "bot_whatsapp.main:app" "--host" "0.0.0.0" "--port" "8001" "--reload"];
          manager = "web";
          env = {
            PORT = "8001";
          };
        };
      };
    };
  };

  # Serviços nativos do Nix para IDX (alternativa ao Docker para dev rápido)
  services = {
    postgres = {
      enable = true;
      package = pkgs.postgresql_15;
      extensions = [ "postgis" ]; # Habilita PostGIS
    };
    redis = {
      enable = true;
    };
    docker = {
      enable = true; # Habilita o daemon do Docker
    };
  };
}
