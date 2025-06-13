! [old Class AION Banner](https://github.com/kamidaki/old-class-server/blob/main/Banner_OldClass.png)

# Tradução PT-BR para Aion (Baseado nas versões 4.x e inferiores)

Esse código foi desenvolvido para trazer a primeira tradução utilizável da língua Brasileira (Português do Brasil). O código foi estruturado apenas para traduzir em massa utilizando o Google Translate, e todo o restante das correções, melhorias e adaptações de textos para coerência ao idioma está sendo feito pelos desenvolvedores. Este projeto é público e pode ser usado por qualquer pessoa, e está aberto a contribuições e melhorias.

Até o momento, o ENU foi totalmente traduzido pelo Google, mas ainda falta corrigir palavras que a IA não consegue encontrar o significado verdadeiro, nem encaixar no contexto, resultando em alguns textos sem sentido. Todos eles precisam ser encontrados e corrigidos manualmente.

O Python foi separado em pastas, pois trata-se de uma automação gratuita que precisa respeitar o limite de requisição, e consegue varrer 100% das linhas, sem deixar nenhuma para trás.

Este arquivo de tradução L10N serve não só para versões 4.x, mas também para versões inferiores. Basta utilizar uma ferramenta de varredura que compare os arquivos da versão traduzida com a versão inferior e remover os arquivos diferenciais.

Também é necessário manter **todos** os arquivos de UI da versão original, pois eles são responsáveis pelo **LAYOUT** de cada versão. Não os troque sem saber o que está fazendo.

Esta tradução foi feita inicialmente para o servidor Old Class. Conheça-o em [https://aionclassicbrasil.com/](https://aionclassicbrasil.com/)

> \ [!TIP]
> Lembre-se que a tradução está sendo melhorada constantemente. Sempre consulte este repositório para saber mais detalhes.

>>**Obs:** Não ensinamos como traduzir, montar servidores ou editar o CLIENT. Este projeto é destinado a pessoas que já sabem como editar o CLIENT e o SERVIDOR.

Para fazer parte da nossa comunidade, visite nosso Discord: [https://discord.gg/SKCVjHd7j9](https://discord.gg/SKCVjHd7j9)

---

## Configuração da Tradução

1. Empacote os arquivos em ZIP e converta para `.pak`, ou utilize um empacotador que gere diretamente o `.pak`. Alguns clientes, como o Client Old Class, aceitam a conversão manual.
2. Renomeie o arquivo `.pak` para `z_idiomaPTBR.pak` e copie-o para o diretório: `\l10n\ENU\Data`
3. Não é necessário excluir o `data.pak` original, pois o cliente carrega os arquivos em ordem alfabética e usa o último arquivo lido.
4. Abra o jogo e teste.
