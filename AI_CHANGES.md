# Registo de alterações

## 2026-09-08 — distribuição independente 0.5.0

- Origem: Bridge 0.4.1, revisão `92c4151f308dd0b768475a45b4de3e2b0660359c`.
- Nova pasta/repositório; sem copiar configurações pessoais, credenciais, túneis ou ambientes virtuais.
- Instaladores Linux/PowerShell, configuração preservada e ambiente Blender separado.
- Adaptadores X11/Windows, pesquisa Windows com proteção de caminhos e diagnóstico local.
- Windows recusa shell/Git/patch sem isolamento e recusa fecho que fingisse ser gracioso.
- Guias em português: instalação, versões/ativação Unity e Blender, ligação manual ao ChatGPT.
- 40 testes passaram em Ubuntu 26.04/Python 3.14.4 com `BRIDGE_SANDBOX_TESTS=1`
  e `BRIDGE_SYSTEMD_TESTS=1`, sem skips. Incluem sessão MCP stdio real (20 ferramentas),
  negação de caminho fora do workspace, Bubblewrap, commit Git isolado e persistência de
  aplicação após parar o serviço lançador.
- Corrigida uma dependência do teste de lifecycle na configuração local antiga: agora
  passa a configuração temporária explicitamente ao subprocesso de teste.
- `pip check` da Bridge sem dependências quebradas; ambiente Blender instalado separadamente.
- CI Ubuntu/Windows criada; capturas reais, editores e ligação ChatGPT desta cópia ainda
  precisam da aceitação manual documentada em VALIDATION.md.
- O addon vendorizado mantém os bytes e espaços do upstream, com licença e proveniência.
- A primeira CI Windows revelou comparação entre caminhos temporários curtos (8.3)
  e caminhos canónicos. A raiz é agora normalizada antes de validar/converter caminhos.
- O wrapper Blender foi importado no novo ambiente e anunciou 30 ferramentas, sem
  iniciar uma sessão no editor. O hash do addon corresponde à referência original.
- CI Windows passou em Python 3.12 e 3.14 após a correção de caminhos (run 34217861245).
  Uma corrida no teste Linux de processos foi detetada: o teste sinalizava antes de
  `/proc` identificar o executável final. O teste aguarda agora o arranque; a política
  de autorização de processos continua estrita.

## 2026-09-08 — Variante independente PC Bridge Linux

Pedido: preservar PCBridgePortable e criar noutra pasta um instalador só para Linux,
com instruções para o utilizador. Base copiada sem Git, venvs ou configuração pessoal.

Alterações: install.sh/setup_bridge.py com recusa de outros sistemas/root/WSL,
pré-verificação Bubblewrap e dependências, validação de caminhos antes de instalar,
configuração privada e preservada, pip check e doctor no final, exemplo MCP local.
run_bridge.py recusa outros SOs. CI apenas Ubuntu. README e guias com instalação,
uso, configuração de editores/conta, diagnóstico, atualização e remoção; removido
install.ps1 nesta cópia. package.sh gera arquivo distribuível e SHA-256.

Validação: instalação nova com --with-blender numa pasta com espaços e repetição
com configuração preservada; 49 testes passaram no anfitrião (Bubblewrap/systemd
incluídos). Comparação SHA-256 dos 31 ficheiros da base: inalterados. As falhas dos
testes novos em pasta já configurada foram corrigidas. Ver VALIDATION.md para os
limites de validação gráfica, editores, conta remota e outras distribuições.

## 2026-09-08 — Preparação de publicação pública

Pedido: criar um repositório público na conta SomeGuySomewhereSometime, com nome
claro e apresentação do propósito. Nome escolhido: pc-bridge-linux. README
expandido com funcionalidades, casos de utilização, requisitos e limites de acesso;
guia de instalação inclui clone do novo repositório. Preservadas as licenças e
atribuições existentes, sem atribuir uma licença nova ao código da Bridge.
Conteúdo de distribuição revisto para excluir configuração pessoal, credenciais,
venvs e histórico Git da origem. A publicação inclui apenas esta variante Linux.
