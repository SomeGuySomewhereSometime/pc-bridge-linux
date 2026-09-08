# Unity e Blender: preparação manual

As versões abaixo são a referência da instalação de origem, lida a 8 de setembro
de 2026. Não significam que todas as combinações de versões/sistemas foram testadas.

| Componente | Referência |
|---|---|
| Unity Editor | 6000.6.0f1 |
| AI Game Developer / Unity MCP | 0.90.0 |
| GameDev MCP Server gerido pelo plugin | 9.2.5 |
| Blender | 5.2.1 LTS |
| Blender addon incluído | 1.6, protocolo 5 |
| Blender MCP Python | 1.9.1, MCP SDK 1.30.0 |
| Bridge Python MCP SDK | 2.2.0, ambiente separado |

## Unity

1. Instale Unity Hub e um Editor compatível com o seu projeto/SO. Consulte
   `ProjectSettings/ProjectVersion.txt` de cada projeto; abrir numa versão diferente
   pode fazer migração. Use uma cópia do projeto para testar a integração.
2. Instale **AI Game Developer**. O [guia do autor](https://github.com/IvanMurzak/Unity-MCP/wiki/Installation-Guide)
   descreve instalação por unitypackage, OpenUPM ou Package Manager. A documentação
   indica Unity 2022.3 como mínimo, mas a referência desta cópia é Unity 6000.6.0f1.
   Prefira um caminho do projeto sem espaços, conforme o guia do plugin.
3. Para reproduzir a referência, registe OpenUPM com os scopes indicados em
   `ops/config/unity/packages-mcp.json` e selecione `com.ivanmurzak.unity.mcp` 0.90.0.
   O JSON é referência para mesclar, **não substitui** `Packages/manifest.json` nem
   `packages-lock.json` de um projeto existente. As extensões são opcionais: Input
   System, Animation, ProBuilder, Cinemachine, Navigation, Splines e Particle System;
   ative apenas as necessárias e confira as dependências Unity resolvidas.
4. Abra `Window > AI Game Developer`, aguarde compilação/download do servidor e confirme
   ligação ativa. Mantenha `keepConnected`/`keepServerRunning` ativos se quiser continuidade.
   A [configuração oficial](https://github.com/IvanMurzak/Unity-MCP/wiki/Configuration)
   fica em `UserSettings/AI-Game-Developer-Config.json`. Anote o endereço/porto reais
   do projeto; o servidor acompanha a versão do plugin, não o atualize isoladamente.
5. Na lista de ferramentas, confirme pelo menos `scene-list-opened`,
   `editor-application-get-state`, `console-get-logs`, `screenshot-game-view` e
   `screenshot-scene-view`. Ferramentas instaladas ou skills geradas não provam que
   estão enabled. Ative apenas as capacidades que quer disponibilizar.
6. Configure o cliente MCP pela janela do plugin. Para túnel, use o endpoint HTTP
   MCP local que a configuração efetiva indicar (transport `streamableHttp`, caminho
   `/mcp` quando indicado). Não exponha um endpoint sem autenticação fora de loopback.
7. Confirme por MCP: projeto correto, cenas abertas, estado do Editor e Console.
   Para trabalho de gameplay, faça ainda Play Mode e inspeção da Game View; compilar
   não basta. Teste só numa cena descartável e guarde o projeto conscientemente.

O Unity precisa de licença/ativação e módulos de build escolhidos no Hub pelo utilizador.
O instalador desta Bridge não resolve licenças, migra projetos ou ativa ferramentas.

## Blender

1. Instale Blender para Linux. Execute `--with-blender` no instalador desta cópia;
   cria `.venv-blender` com dependências próprias. Não misture MCP 1.x do Blender com
   MCP 2.x da Bridge.
2. Em Blender, `Edit > Preferences > Add-ons`, use **Install from Disk** (ou **Install**,
   conforme a versão) e selecione `ops/vendor/blender-mcp/blender_mcp.py`. Ative
   **MCP for Blender** e guarde as preferências. Esta cópia inclui o addon correspondente
   à referência; não descarregue silenciosamente um addon diferente do servidor.
3. Na viewport 3D, prima `N`, abra **MCP for Blender** e inicie o servidor. Confirme
   loopback `127.0.0.1`, porta `9876` e ausência de erros. O [guia do autor](https://github.com/ahujasid/blender-mcp)
   descreve a instalação e o painel. Se optar por auto-start, guarde essa opção e
   teste uma reabertura: pode depender da cena/preferências.
4. Recursos externos como Sketchfab, Poly Haven e geração 3D são opcionais e podem
   exigir contas/chaves próprias. Não são necessários para ler a cena ou executar
   código Blender. O wrapper desativa telemetria do servidor; reveja também o
   consentimento do addon nas preferências.
5. Configure o cliente/túnel stdio com o Python da `.venv-blender` e argumento absoluto
   `ops/blender_entry.py`. O Python está em `.venv-blender/bin/python`. Mantenha Blender aberto com o addon ativo. Não lance o servidor Python
   dentro da consola Python do Blender.
6. Peça `get_context`, `get_scene_objects` e uma captura da viewport. Confirme nome da
   cena, ficheiro e objetos antes de editar. Não confunda processo/túnel ativo com addon
   ligado. Use ficheiros de teste e confirme visualmente quaisquer alterações.

O addon permite executar Python com as permissões do utilizador. O consentimento de
scripts/addon é manual; não desative globalmente proteções do Blender para contornar erros.
