# PC Bridge Linux

**Ligue um cliente de inteligência artificial compatível com MCP ao seu computador Linux
para trabalhar com ficheiros, comandos e projetos locais.** Inclui um instalador por
utilizador e guias para integrar Unity, Blender e ChatGPT.

MCP (Model Context Protocol) é o protocolo que permite ao cliente descobrir e chamar
as ferramentas da Bridge. O projeto não inclui um modelo de IA: precisa de um cliente
MCP e, para usar ChatGPT remotamente, de configurar a sua própria ligação/túnel.

## O que faz

- Disponibiliza **20 ferramentas MCP** para operações de ficheiros, pesquisa,
  comandos, Git, diagnóstico do computador e gestão de aplicações autorizadas.
- Executa shell, Git e patches com **Bubblewrap**, com acesso limitado ao workspace
  e às regras de proteção configuradas, sem rede na sandbox dos comandos.
- Inclui captura do ecrã para sessões Wayland ou X11, sujeita às permissões do desktop.
- Prepara opcionalmente um ambiente Python separado para o **Blender MCP**, com addon incluído.
- Documenta a configuração do **Unity MCP** no próprio projeto e a ligação dos três
  servidores ao cliente. A Bridge, Unity e Blender mantêm responsabilidades separadas.

## Porquê usar

É útil quando quer que um assistente trabalhe nos seus projetos Linux através de
ferramentas explícitas, sem copiar ficheiros e resultados de comandos a cada interação.
Por exemplo: investigar um erro num projeto, editar ficheiros numa pasta autorizada,
consultar o estado do Git ou combinar trabalho de código com ferramentas dos editores.

A instalação fica numa pasta independente, usa ambientes Python próprios e preserva
a configuração quando volta a executar o instalador. Pode experimentar a integração
sem substituir uma instalação anterior, com passos claros para diagnosticar e remover.

O workspace é a pasta onde permite ao assistente trabalhar: as ferramentas podem
alterar e apagar ficheiros dentro dela. Escolha os projetos que quer disponibilizar
e configure os caminhos protegidos. O isolamento é uma fronteira de desenvolvimento,
não uma garantia de contenção contra processos hostis da mesma conta local. Os MCPs
dos editores têm as suas próprias permissões, incluindo execução de código no Editor.

## Compatibilidade

**Testado em Ubuntu 26.04 LTS, Python 3.14.4 e systemd 259.** Outras distribuições
Linux podem funcionar se cumprirem os requisitos, mas ainda não foram validadas.
Requer Python 3.12+, venv, Git e Bubblewrap funcional. O lançamento de aplicações
requer systemd de utilizador compatível; as capturas requerem uma sessão gráfica.
Windows, macOS e WSL são recusados por este instalador.

## Começar

Num sistema Ubuntu/Debian com Python 3.12 ou superior, instale os requisitos
e obtenha esta cópia numa pasta permanente do seu utilizador:

```sh
sudo apt install python3 python3-venv git bubblewrap
git clone https://github.com/SomeGuySomewhereSometime/pc-bridge-linux.git PCBridgeLinux
cd PCBridgeLinux
sh install.sh --check
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects"
.venv/bin/python run_bridge.py doctor
```

O `sudo` é usado apenas pelo gestor de pacotes; execute o instalador sem sudo.
Para incluir o ambiente Python do Blender, acrescente `--with-blender`.
A instalação descarrega dependências Python e mantém as versões fixadas da base.

**[Instruções completas para o utilizador](docs/INSTALL.md)** ·
[Unity e Blender](docs/EDITORS.md) · [Cliente MCP e ChatGPT](docs/CHATGPT.md) ·
[Validação e limitações](VALIDATION.md)

O instalador gera `.local/mcp-client.json` com caminhos absolutos para clientes que
aceitam `mcpServers`. Não é preciso ativar a venv. A ligação à conta/túnel e a
ativação de addons nos editores são passos manuais descritos nos guias.

## Âmbito

- Linux nativo, Wayland ou X11. Windows, macOS e WSL são recusados no instalador.
- Shell, Git e patches exigem Bubblewrap funcional; sem ele a instalação completa para.
- Captura Wayland depende do portal e do consentimento da sessão gráfica; X11 usa MSS.
- Lançar aplicações exige systemd de utilizador compatível; pode abrir os editores manualmente.
- Configuração existente é preservada. A pasta de projetos é separada da instalação.
- Não instala serviços nem altera contas, outros projetos ou instalações anteriores.

## Proveniência

Derivado da cópia local de PCBridgePortable em 08-09-2026. As alterações desta
variante concentram-se no instalador, ponto de entrada, documentação e CI Linux.
Os módulos partilhados mantêm adaptadores internos da base e respetivos testes;
isso não representa suporte a Windows nesta distribuição.
O addon Blender conserva a [licença MIT original](ops/vendor/blender-mcp/LICENSE).
A base não define uma licença de redistribuição para o código da Bridge.

## Empacotar

Execute `sh package.sh` para gerar `PCBridgeLinux.tar.gz` e o respetivo SHA-256 na
pasta acima. O pacote inclui código, documentação e addon; exclui venvs, configuração
pessoal, `.local` e histórico Git. Distribua esse pacote, não uma instalação configurada.
