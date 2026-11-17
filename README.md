# Sistema gestão de hotel

## Links

- Trello: https://trello.com/b/XJtjmbJN/sistema-gestao-hotelaria-projeto-fullstack-i
- tldraw: https://www.tldraw.com/f/oHepfPirDX1sJoulEcaNT?d=v-1250.-465.2840.1624.page
- UI: https://app.flowstep.ai/file?activeFileId=002497e9-0c27-4899-8159-31c24d1908cd

## Como rodar localmente

### Dados para apresentação

Depois de configurar o banco e executar `python manage.py migrate`, rode:

```powershell
python manage.py popular_demo
```

O comando cria tipos, tarifas, quartos, clientes, reservas e ocorrências fictícios. Também prepara os seis funcionários já usados no sistema, criando os que faltarem e definindo a senha `Senha99@` para todos. Os usuários `Cozinheiro`, `Recepcionista`, `Gerente` e `Camareira` ficam ativos; `gregory` e `KeenanYuri` continuam inativos. O administrador separado não é alterado.

O comando pode ser executado novamente sem duplicar os registros de demonstração. As chegadas e saídas são calculadas a partir da data local; para preparar uma apresentação em outra data, use `python manage.py popular_demo --data-base AAAA-MM-DD`. Executar novamente atualiza as datas e os dados desses registros fictícios e redefine a senha dos funcionários.

### Limpar os dados

Para remover todos os cadastros do hotel, usuários que não sejam superusuários, grupos, sessões e registros de administração:

```powershell
python manage.py limpar_banco --confirmar
```

A limpeza é permanente. Os superusuários e suas senhas são preservados, assim como a estrutura do banco, migrações, tipos de conteúdo e permissões do Django. Depois, `python manage.py popular_demo` recria os dados da apresentação.
