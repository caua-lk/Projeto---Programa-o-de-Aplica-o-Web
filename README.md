# Agenda de Atividades 

## Proposta 
O nosso projeto propõe utilizar uma aplicação simples e intuitiva para a organização e agendamento de atividades decorrentes do cotidiano do usuário, uma vez que o mesmo necessita de orientação para estabelecer tópicos que serão resolvidos, podendo: alterar, adicionar, excluir, finalizar e mostrar. 
## Justificativa 	
A proposta de utilizar uma aplicação simples e intuitiva para a organização e agendamento de atividades cotidianas advém pela necessidade de oferecer uma estrutura eficiente, flexível e com orientação simples.
## Gerenciamento de Sessões
Para fazer a ponte entre o banco de dados e a navegação do usuário, o projeto utiliza o sistema de session. Como o protocolo web não guarda o histórico de quem está acessando, a sessão é usada para manter o usuário conectado enquanto ele navega pelo sistema. Aproveitando também para pegar o id e nome do usuário para captar somente os dados cabíveis do usuário atual.
## Banco de Dados 
O banco de dados utilizado foi o Sqlite3, onde o sistema procura o usuário e atividades relacionadas de maneira coerente às privacidades de usuário. 
### Estrutura das Tabelas
#### Tabela: `Users`
| Campo | Tipo de Dado | Atributos |
| :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `nome` | TEXT | UNIQUE |
| `senha` | TEXT | NOT NULL |

#### Tabela: `Tarefa`
| Campo | Tipo de Dado | Atributos |
| :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `nome` | TEXT | NOT NULL |
| `descricao` | TEXT | - |
| `prazo` | TEXT | - |
| `user_id` | INTEGER | FOREIGN KEY (Users.id) |
**Componentes:**
- Arthur Moreira Barros
- Cauã Vitor Costa da Silva
- Daniel dos Santos Soares