# Ligar os três MCPs

## Primeiro, verificar localmente

Execute `run_bridge.py doctor` com o Python da `.venv`. Para um cliente MCP local,
configure o executável absoluto `.venv/bin/python`
e os argumentos absolutos `run_bridge.py`, `stdio`. A pasta de trabalho do cliente
pode ser qualquer uma. O programa não abre uma porta HTTP pública.

Para Blender, use o Python de `.venv-blender` com `ops/blender_entry.py`; para Unity,
use a configuração gerada pelo plugin do projeto. São três servidores independentes.

Exemplo de entrada para clientes que aceitam `mcpServers` (substitua os caminhos):

```json
{
  "mcpServers": {
    "pcbridge": {
      "command": "/absolute/PCBridgeLinux/.venv/bin/python",
      "args": ["/absolute/PCBridgeLinux/run_bridge.py", "stdio"]
    },
    "blender": {
      "command": "/absolute/PCBridgeLinux/.venv-blender/bin/python",
      "args": ["/absolute/PCBridgeLinux/ops/blender_entry.py"]
    }
  }
}
```

O instalador gera este exemplo com caminhos reais em `.local/mcp-client.json`.
Não cole esta estrutura num cliente com outro esquema; adapte os campos desse cliente.

## ChatGPT: parte manual da conta

Referências oficiais consultadas em 08-09-2026. A disponibilidade depende da conta.

Segundo o [guia oficial de ligação](https://developers.openai.com/plugins/deploy/connect-chatgpt):
ative Developer mode em Settings > Security and login, se permitido pela conta.
Em Plugins, crie uma ligação e selecione Tunnel. Reveja as ferramentas e inicie
uma conversa com a ligação ativa. Depois de mudanças de metadados, use Refresh.

O [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
exige túnel, chave de execução e associação à organização/workspace corretos.
Cada pessoa cria os seus; este repositório não fornece identidades partilhadas.
Descarregue o cliente para o seu SO através do guia e consulte `tunnel-client help quickstart`.

Exemplo Linux, depois de disponibilizar a chave conforme o guia:

```sh
tunnel-client init --sample sample_mcp_stdio_local --profile pcbridge-linux --tunnel-id SEU_TUNNEL_ID --mcp-command '/absolute/PCBridgeLinux/.venv/bin/python /absolute/PCBridgeLinux/run_bridge.py stdio'
tunnel-client doctor --profile pcbridge-linux --explain
tunnel-client run --profile pcbridge-linux
```

Se a pasta de instalação contém espaços, coloque cada caminho entre aspas
dentro do valor de `--mcp-command`, conforme a sintaxe do cliente instalado.

Para Blender configure outro perfil stdio; para Unity, um perfil com
`--mcp-server-url` apontado ao endpoint MCP local. Mantenha cada cliente ativo.
Túneis privados não equivalem à publicação de um plugin público.

## Evitar colisões nesta instalação

Escolha nomes novos para todos os perfis. Se executar vários clientes de túnel,
atribua portas de diagnóstico diferentes nas configurações geradas, conforme o
`help` da versão instalada. Não reutilize os perfis, IDs, portas administrativas
ou serviços da instalação anterior deste PC.

Guarde chaves fora do Git e fora do workspace autorizado; não as inclua na linha de
comando nem num README. Se criar arranque automático, configure o processo do túnel,
não o servidor stdio isolado: sem um cliente a ler/escrever, stdio não presta serviço.
Use uma unidade systemd de utilizador com o caminho da configuração nova.
Esse passo é manual e deve ser testado após login antes de ser considerado concluído.

## Teste final por pessoa

1. Bridge: listar o workspace e ler um ficheiro de teste; uma leitura fora dele deve falhar.
2. Unity: identificar o projeto, cenas e estado do Editor; ler Console e obter Game View.
3. Blender: identificar cena, objetos e ficheiro; obter viewport.
4. Verificar captura no desktop e, numa pasta/cena descartável, uma alteração reversível.
5. Parar/reiniciar apenas a ligação nova e confirmar que os editores permanecem abertos.

Não declare sucesso apenas porque um túnel está online ou uma porta está aberta.
