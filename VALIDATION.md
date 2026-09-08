# Validação da variante Linux — 08-09-2026

## Executado nesta tarefa

- Instalação completa numa pasta temporária com espaços no nome, com venvs novas,
  downloads das dependências fixadas e `--with-blender`: sucesso.
- `pip check` passou nos ambientes da Bridge e do Blender.
- `run_bridge.py doctor`: executado pelo instalador com sucesso.
- Segunda execução do instalador: configuração preservada byte a byte; um novo
  argumento de workspace foi ignorado e essa pasta não foi criada.
- 49 testes passaram com Python 3.14 no Linux anfitrião, sem testes omitidos,
  com `BRIDGE_SANDBOX_TESTS=1 BRIDGE_SYSTEMD_TESTS=1`.
- Inclui sessão MCP stdio real, 20 ferramentas, recusa de leitura fora do workspace,
  isolamento Bubblewrap, Git e sobrevivência de aplicação ao fim do seu lançador.
- Inclui 9 testes novos do instalador: recusa de outros SOs/root/WSL, validação antes
  de alterações, privacidade, preservação da configuração e caminhos com espaços.
- Os 31 ficheiros da base original foram comparados por SHA-256: nenhum alterado.

A tentativa inicial dentro da sandbox da tarefa não podia criar namespaces
Bubblewrap e teve timeout na inicialização MCP. A validação completa foi executada
no anfitrião, mantendo o isolamento próprio da Bridge. Foram corrigidos dois testes
novos que pressupunham uma pasta de instalação sem configuração prévia.

## Ainda não validado

- Instalação em outras distribuições, Python 3.12 ou outras arquiteturas. A CI
  incluída destina-se a Ubuntu/Python 3.12 e 3.14; não foi executada remotamente.
- Captura gráfica real Wayland/X11 desta cópia (os testes verificam os adaptadores).
- Uma nova conta/túnel ChatGPT, Unity em Play Mode ou addon Blender ligado a esta cópia.
- Reinício do computador/login e arranque automático. O pacote não instala serviços.

A instalação do ambiente Blender não prova a ligação ao Editor. Uma porta aberta
não prova a identidade do projeto/cena nem o funcionamento das ferramentas.
