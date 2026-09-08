# Guia do utilizador — Linux

## 1. Preparar o computador

Use Linux nativo e um terminal da sua sessão de utilizador. Confirme:

```sh
python3 --version
echo "$XDG_SESSION_TYPE"
```

Python tem de ser 3.12 ou superior. A sessão gráfica pode ser `wayland` ou `x11`.
A Bridge funciona sem desktop para ficheiros/comandos; capturas exigem sessão gráfica.
Windows, macOS e WSL não são alvos deste pacote.

Em Ubuntu/Debian, instale os requisitos do sistema:

```sh
sudo apt install python3 python3-venv git bubblewrap
```

A distribuição tem de disponibilizar Python 3.12+. Instale o pacote venv da versão
Python que está a utilizar. Noutras distribuições use os pacotes equivalentes;
esta base espera os utilitários Linux em `/usr/bin`.

Para capturas Wayland:

```sh
sudo apt install python3-dbus python3-gi xdg-desktop-portal
```

É também necessário o backend do seu desktop: por exemplo,
`xdg-desktop-portal-gnome` no GNOME ou `xdg-desktop-portal-kde` no KDE. Use apenas o
apropriado. O helper de captura usa `/usr/bin/python3` e os módulos do sistema.
Para X11, precisa de `libx11-6` e das variáveis `DISPLAY`/`XAUTHORITY` da sessão.

## 2. Extrair e instalar

Extraia `PCBridgeLinux.tar.gz` com o gestor de arquivos para uma pasta permanente,
por exemplo `~/Aplicacoes/PCBridgeLinux`. Em alternativa, obtenha o código com:

```sh
git clone https://github.com/SomeGuySomewhereSometime/pc-bridge-linux.git PCBridgeLinux
cd PCBridgeLinux
```

Abra um terminal dentro da pasta que contém `install.sh` e execute:

```sh
sh install.sh --check
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects"
```

Não use sudo no instalador. A pasta de projetos pode já conter os seus projetos,
mas deve estar separada da instalação. Não use a pasta pessoal inteira nem `/`.
Sem `--workspace`, o destino é `~/PCBridgeLinuxProjects`.
O download Python requer acesso à Internet/PyPI (ou ao índice pip configurado).

Se também vai utilizar Blender, use:

```sh
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects" --with-blender
```

São criados nesta instalação:

| Caminho | Conteúdo |
|---|---|
| `.venv/` | Python e dependências da Bridge |
| `.venv-blender/` | Ambiente separado, apenas com `--with-blender` |
| `bridge_config.json` | Pasta autorizada, política de ficheiros e aplicações |
| `.local/` | Dados privados desta instalação |
| `.local/mcp-client.json` | Exemplo MCP com os caminhos reais desta cópia |

A pasta de projetos é criada se não existir. O instalador verifica dependências
Python e executa o diagnóstico. Não cria serviços, perfis de túnel ou contas.
Uma interrupção pode deixar a venv parcial; corrija a causa e repita o mesmo comando.

## 3. Verificar e ligar

```sh
.venv/bin/python run_bridge.py doctor
.venv/bin/python -B check.py
```

O diagnóstico mostra requisitos e portas locais, não prova que um Editor está
pronto. Os testes normais usam dados descartáveis; alguns testes de integração
ficam omitidos. Para testar também o isolamento e o lançador systemd nesta máquina:

```sh
BRIDGE_SANDBOX_TESTS=1 BRIDGE_SYSTEMD_TESTS=1 .venv/bin/python -B check.py
```

Esses testes criam processos e unidades temporárias de teste; não usam os seus editores.
Para ligar o cliente, siga [MCP e ChatGPT](CHATGPT.md). Para os editores, siga
[Unity e Blender](EDITORS.md). A Bridge disponibiliza 20 ferramentas MCP.

## 4. Configuração e utilização diária

O cliente MCP inicia `run_bridge.py stdio` com o Python da `.venv`. Executá-lo
sozinho num terminal pode ficar à espera: stdio precisa de um cliente MCP.
Depois de alterar o JSON, reinicie apenas a ligação desta cópia.

Na primeira instalação pode registar aplicações:

```sh
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects" \
  --blender /usr/bin/blender
```

Use o caminho de um executável que exista no seu computador. Para Unity acrescente
`--unity /caminho/Editor/Unity --unity-project /caminho/do/projeto`;
o projeto deve estar dentro do workspace. Use aspas em caminhos com espaços.

Depois da instalação, edite `applications` em `bridge_config.json` manualmente.
O instalador não substitui o JSON nem aplica novos argumentos de workspace/aplicações.
Para Blender Snap ou lançadores especiais, abra o Editor manualmente ou configure
explicitamente executável, argumentos fixos e identidade do processo.
Não ative argumentos livres em shells ou interpretadores.

O workspace permite alterações aos projetos que contém. Guarde chaves e outros
segredos fora dele ou acrescente os caminhos a `filesystem.denied_paths`.
`workspace/.secrets` já fica bloqueado por defeito. Não partilhe `.local` nem o JSON
pessoal ao distribuir o pacote.

## 5. Resolver problemas

| Problema | Ação |
|---|---|
| Python antigo / falta venv ou ensurepip | Instalar Python 3.12+ e o pacote venv correspondente |
| Falha pip ou download | Verificar rede/índice e repetir o comando; não há sucesso enquanto pip/doctor falharem |
| Bubblewrap não cria sandbox | Executar num Linux nativo; verificar suporte a user namespaces e política da distribuição. Não desativar o isolamento |
| `systemctl --user` indisponível | Usar a sessão normal do utilizador ou abrir editores manualmente |
| Opções systemd não reconhecidas | O lançador usa `--expand-environment=no` e `ExitType=cgroup`; em systemd antigo abrir os editores manualmente |
| Captura Wayland falha | Verificar portal/backend, dbus/gi do sistema e consentimento na sessão gráfica |
| Captura X11 falha | Verificar sessão ativa, libX11 e DISPLAY/XAUTHORITY |
| Porta de Editor não responde | Abrir o Editor e ativar o plugin/addon; rever a porta em `integrations` |
| Cliente usa caminhos antigos | Se moveu a pasta, recriar as venvs e corrigir o JSON do cliente; prefira instalar logo no destino definitivo |

`--check` não instala nem cria configuração. `--configure-only` cria apenas a
configuração e a pasta de projetos; não prova que dependências, sandbox ou MCP funcionam.

## 6. Repetir, atualizar e remover

Pode repetir o instalador na mesma pasta: mantém `bridge_config.json` e o exemplo
MCP existente. Ao adicionar Blender mais tarde, acrescente a entrada do Blender ao
cliente conforme [EDITORS.md](EDITORS.md). Para mudar de workspace edite o JSON.

Para uma nova versão, extraia numa pasta nova, instale e teste antes de trocar a
ligação no cliente. Conserve a pasta anterior até verificar o resultado.

Para remover, desligue esta ligação no cliente MCP e pare apenas o túnel/perfil
que criou para ela, se existir. Remova as respetivas entradas do cliente. Depois
apague a pasta desta instalação com o gestor de ficheiros. A pasta de projetos
fica separada: conserve-a. Addons ou serviços que tenha instalado manualmente
precisam de ser removidos nas respetivas aplicações, se já não forem necessários.
