from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Category, Field, User, Shepherd, Church
from django.contrib.auth.hashers import make_password
import json


class Command(BaseCommand):
    help = 'Cria dados iniciais do sistema (categorias)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se as categorias já existirem',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando criação de dados iniciais...')
        )

        # Dados dos campos (fields)
        fields_data = [
            {"name": "Canoinhas"},
            {"name": "Porto União"},
            {"name": "São Paulo"},
            {"name": "Curitiba"},
            {"name": "Mafra"},
            {"name": "Itaiopolis"},
            {"name": "Jaraguá do Sul"},
            {"name": "São Joaquim"},
            {"name": "Itajaí"},
            {"name": "Navegantes"},
            {"name": "Camboriú"},
            {"name": "Rio Grande do Sul"},
            {"name": "Foz do Iguaçu"},
            {"name": "Rio do Sul"},
            {"name": "Campos Novos"},
            {"name": "São Bento do Sul"},
            {"name": "Rio Negrinho"},
            {"name": "Doutor Pedrinho"},
            {"name": "Blumenau"},
            {"name": "Penha"},
            {"name": "Barra Velha"},
            {"name": "Joinville"},
            {"name": "Tesouraria Geral"},
            {"name": "Três Barras"}
        ]

        # Dados dos usuários
        users_data = [
            {
                "email": "Israelbruna0@gmail.com",
                "first_name": "Bruna",
                "last_name": "dos Santos Colaço",
                "username": "bruna.colaco",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "password_changed": True
            },
            {
                "email": "Lirian.floriano2018@gmail.com",
                "first_name": "Lirian",
                "last_name": "Nara Floriano de Lima",
                "username": "lirian.floriano",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "password_changed": True
            },
            {
                "email": "eventosnacoesscanoinhas@gmail.com",
                "first_name": "Jamille",
                "last_name": "Santos Bahia Costa",
                "username": "jamille.costa",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "marconascimento381@gmail.com",
                "first_name": "Marco",
                "last_name": "Antonio do Nascimento",
                "username": "marco.nascimento",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "tatiiane.andrade@gmail.com",
                "first_name": "Tatiane",
                "last_name": "Micheli de Andrade Andruchechen",
                "username": "tatiane.andrade",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "fatimaevangelista.nacoes@gmail.com",
                "first_name": "Fátima",
                "last_name": "Silva Macalli",
                "username": "fatima.macalli",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "tesourariakatlin@gmail.com",
                "first_name": "Katlin",
                "last_name": "Caroline da Silva Lemos",
                "username": "katlin.lemos",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "mariliaelizabeti.23@gmail.com",
                "first_name": "Marilia",
                "last_name": "Elizabete Teixeira da Silva",
                "username": "marilia.silva",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "cristinaveiga025@gmail.com",
                "first_name": "Cristina",
                "last_name": "Veiga Bueno",
                "username": "cristina.bueno",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": False
            },
            {
                "email": "rafaelaneuber@gmail.com",
                "first_name": "Rafaela",
                "last_name": "Cristine Neuber",
                "username": "rafaela.neuber",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": False
            },
            {
                "email": "mirianfamilia84@gmail.com",
                "first_name": "Mirian",
                "last_name": "Silva Budal Floriano",
                "username": "mirian.floriano",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "Ricardoadri.oliveira@gmail.com",
                "first_name": "Ricardo",
                "last_name": "Silva de Oliveira",
                "username": "ricardo.oliveira",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "crislainecris0107@outlook.com",
                "first_name": "Crislaine",
                "last_name": "de Oliveira",
                "username": "crislaine.oliveira",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "annafleit200@gmail.com",
                "first_name": "Ana Cláudia",
                "last_name": "Fleit dos Santos",
                "username": "ana.fleit",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "matheus.anderle@hotmail.com",
                "first_name": "Matheus",
                "last_name": "Anderle",
                "username": "matheus.anderle",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "nayarabr691@gmail.com",
                "first_name": "Nayara",
                "last_name": "de Oliveira Brito",
                "username": "nayara.brito",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            },
            {
                "email": "bruna.00.andrade@gmail.com",
                "first_name": "Bruna",
                "last_name": "Andrade Padilha",
                "username": "brunaandradepadilha",
                "role": "treasurer",
                "is_staff": False,
                "is_superuser": False,
                "password_changed": True
            }
        ]

        # Dados das categorias
        categories_data = [
            {
                "name": "Aluguel Sala",
                "mandatory_proof": True
            },
            {
                "name": "Aluguel  Sala e Casa Pastoral",
                "mandatory_proof": True
            },
            {
                "name": "Aluguel Casa Pastoral",
                "mandatory_proof": True
            },
            {
                "name": "Fatura de Água",
                "mandatory_proof": True
            },
            {
                "name": "Fatura de Luz",
                "mandatory_proof": True
            },
            {
                "name": "Cota Telefone",
                "mandatory_proof": True
            },
            {
                "name": "Cota Combustível",
                "mandatory_proof": True
            },
            {
                "name": "Taxa de Lixo",
                "mandatory_proof": True
            },
            {
                "name": "Taxa IPTU",
                "mandatory_proof": True
            },
            {
                "name": "DocumentoS de Carro/ Moto/Caminhão",
                "mandatory_proof": True
            },
            {
                "name": "Peças de Carro/ Moto/Caminhão",
                "mandatory_proof": True
            },
            {
                "name": "Adiantamento Ajuda de Custo",
                "mandatory_proof": True
            },
            {
                "name": "Ajuda de Custo",
                "mandatory_proof": True
            },
            {
                "name": "Retirada",
                "mandatory_proof": True
            },
            {
                "name": "Dizimo Pix",
                "mandatory_proof": True
            },
            {
                "name": "Pix Saída",
                "mandatory_proof": True
            },
            {
                "name": "Dizimo",
                "mandatory_proof": True
            },
            {
                "name": "Voto",
                "mandatory_proof": True
            },
            {
                "name": "Oferta",
                "mandatory_proof": True
            },
            {
                "name": "Sucot",
                "mandatory_proof": True
            },
            {
                "name": "Missão dos 70",
                "mandatory_proof": True
            },
            {
                "name": "Entrada De Tesouraria",
                "mandatory_proof": True
            },
            {
                "name": "Oferta Pix",
                "mandatory_proof": True
            },
            {
                "name": "Voto Pix",
                "mandatory_proof": True
            },
            {
                "name": "Cheque",
                "mandatory_proof": True
            }
        ]

        # Criar campos primeiro
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🏗️  Criando campos...')
        )
        self.stdout.write('='*50)

        fields_created_count = 0
        fields_updated_count = 0
        fields_skipped_count = 0

        for field_data in fields_data:
            name = field_data['name']

            # Verificar se o campo já existe
            field, created = Field.objects.get_or_create(
                name=name
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Campo criado: {name}')
                )
                fields_created_count += 1
            else:
                if options['force']:
                    # Atualizar campo existente (neste caso, apenas o nome)
                    field.name = name
                    field.save()
                    self.stdout.write(
                        self.style.WARNING(f'🔄 Campo atualizado: {name}')
                    )
                    fields_updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Campo pulado (já existe): {name}')
                    )
                    fields_skipped_count += 1

        # Criar categorias
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🏷️  Criando categorias...')
        )
        self.stdout.write('='*50)

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for category_data in categories_data:
            name = category_data['name']
            mandatory_proof = category_data['mandatory_proof']

            # Verificar se a categoria já existe
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'mandatory_proof': mandatory_proof,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Criada: {name}')
                )
                created_count += 1
            else:
                if options['force']:
                    # Atualizar categoria existente
                    category.mandatory_proof = mandatory_proof
                    category.save()
                    self.stdout.write(
                        self.style.WARNING(f'🔄 Atualizada: {name}')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Pulada (já existe): {name}')
                    )
                    skipped_count += 1

        # Dados das atribuições de campos aos usuários
        user_fields_data = [
            {"user_id": 4, "field_id": 1},  # Jamille - Canoinhas
            {"user_id": 4, "field_id": 2},  # Jamille - Porto União
            {"user_id": 5, "field_id": 3},  # Marco - São Paulo
            {"user_id": 5, "field_id": 4},  # Marco - Curitiba
            {"user_id": 6, "field_id": 5},  # Tatiane - Mafra
            {"user_id": 6, "field_id": 6},  # Tatiane - Itaiopolis
            {"user_id": 7, "field_id": 7},  # Fátima - Jaraguá do Sul
            {"user_id": 8, "field_id": 8},  # Katlin - São Joaquim
            {"user_id": 9, "field_id": 9},  # Marilia - Itajaí
            {"user_id": 9, "field_id": 10}, # Marilia - Navegantes
            {"user_id": 9, "field_id": 11}, # Marilia - Camboriú
            {"user_id": 10, "field_id": 12}, # Cristina - Rio Grande do Sul
            {"user_id": 11, "field_id": 13}, # Rafaela - Foz do Iguaçu
            {"user_id": 12, "field_id": 14}, # Mirian - Rio do Sul
            {"user_id": 12, "field_id": 15}, # Mirian - Campos Novos
            {"user_id": 13, "field_id": 16}, # Ricardo - São Bento do Sul
            {"user_id": 13, "field_id": 17}, # Ricardo - Rio Negrinho
            {"user_id": 14, "field_id": 18}, # Crislaine - Doutor Pedrinho
            {"user_id": 15, "field_id": 2},  # Ana Cláudia - Porto União
            {"user_id": 16, "field_id": 19}, # Matheus - Blumenau
            {"user_id": 17, "field_id": 20}, # Nayara - Penha
            {"user_id": 4, "field_id": 24},  # Jamille - Três Barras
            {"user_id": 18, "field_id": 5},  # Bruna Andrade - Mafra
            {"user_id": 18, "field_id": 6}   # Bruna Andrade - Itaiopolis
        ]

        # Criar usuários
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('👥 Criando usuários...')
        )
        self.stdout.write('='*50)

        users_created_count = 0
        users_updated_count = 0
        users_skipped_count = 0

        for user_data in users_data:
            email = user_data['email']
            username = user_data['username']
            first_name = user_data['first_name']
            last_name = user_data['last_name']
            role = user_data['role']
            is_staff = user_data['is_staff']
            is_superuser = user_data['is_superuser']
            password_changed = user_data['password_changed']

            # Verificar se o usuário já existe
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'password_changed': password_changed,
                    'password': make_password('nations123456')  # Senha padrão
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuário criado: {first_name} {last_name} ({email})')
                )
                users_created_count += 1
            else:
                if options['force']:
                    # Atualizar usuário existente
                    user.username = username
                    user.first_name = first_name
                    user.last_name = last_name
                    user.role = role
                    user.is_staff = is_staff
                    user.is_superuser = is_superuser
                    user.password_changed = password_changed
                    user.save()
                    self.stdout.write(
                        self.style.WARNING(f'🔄 Usuário atualizado: {first_name} {last_name} ({email})')
                    )
                    users_updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Usuário pulado (já existe): {first_name} {last_name} ({email})')
                    )
                    users_skipped_count += 1

        # Atribuir campos aos usuários
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🔗 Atribuindo campos aos usuários...')
        )
        self.stdout.write('='*50)

        user_fields_created_count = 0
        user_fields_skipped_count = 0

        for user_field_data in user_fields_data:
            user_id = user_field_data['user_id']
            field_id = user_field_data['field_id']

            try:
                user = User.objects.get(id=user_id)
                field = Field.objects.get(id=field_id)
                
                # Verificar se a relação já existe
                if user.fields.filter(id=field_id).exists():
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Relação pulada (já existe): {user.first_name} - {field.name}')
                    )
                    user_fields_skipped_count += 1
                else:
                    # Adicionar campo ao usuário
                    user.fields.add(field)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Campo atribuído: {user.first_name} - {field.name}')
                    )
                    user_fields_created_count += 1
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Usuário não encontrado: ID {user_id}')
                )
            except Field.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Campo não encontrado: ID {field_id}')
                )

        # Dados das igrejas
        churches_data = [
            {"name": "Sede Agua Verde", "address": "Rua Julio Correa da Costa,981", "field_id": 1, "shepherd": "Pr Romulo E Pra Sarita"},
            {"name": "Sede Iririú", "address": "Rua Miguel Zattar, 179, Iririu", "field_id": 22, "shepherd": "Ev Aline e Ev Izaleno"},
            {"name": "Panagua", "address": "Rua Vinte e Cinco de Dezembro, 195, Paranaguamirim", "field_id": 22, "shepherd": "Pb Eder E Miss Fabi"},
            {"name": "Vila Nova", "address": "Bento Torquato da Rocha, 680, Vila Nova Joinville", "field_id": 22, "shepherd": "Ev Sandro e Ev Marcelina"},
            {"name": "Ana Terra", "address": None, "field_id": 4, "shepherd": "Pb Everson e Miss Jeniffer"},
            {"name": "Guaraituba", "address": None, "field_id": 4, "shepherd": "Pb Natan e Miss Luana"},
            {"name": "Sede Mauá", "address": None, "field_id": 4, "shepherd": "Pr Eduardo  e Pra Suelen"},
            {"name": "Pilarzinho", "address": None, "field_id": 4, "shepherd": "Pb Natan e Miss Luana"},
            {"name": "Sede Centro", "address": None, "field_id": 3, "shepherd": "Pr Delmir e Pra Amanda"},
            {"name": "Capitão Brás", "address": None, "field_id": 3, "shepherd": "Pr Delmir e Pra Amanda"},
            {"name": "Sede Brasilia", "address": None, "field_id": 16, "shepherd": "Pr Guilherme e Pra Bruna"},
            {"name": "Centenário", "address": None, "field_id": 16, "shepherd": "Ev Everton e Miss Cris"},
            {"name": "Serra Alta", "address": None, "field_id": 16, "shepherd": "Pb Lucas E Miss Samanta"},
            {"name": "Campo Alegre", "address": None, "field_id": 16, "shepherd": "Pr Leandro"},
            {"name": "Sede Penha", "address": "Rua Paula Simone Leger, 95 Centro, Penha", "field_id": 20, "shepherd": "Ev Adonis e Ev Nayara"},
            {"name": "Cruzeiro", "address": None, "field_id": 16, "shepherd": "Dc Emerson"},
            {"name": "Aventureiro", "address": "Rua Martinho Van Biene,2560 Aventureiro, 89225-450", "field_id": 22, "shepherd": "Pb Hugo e Miss Fernanda"},
            {"name": "Sede Itoupava", "address": "Rua Tunapolis, 91 , Itoupava Central", "field_id": 19, "shepherd": "Pr Giovani  e Pra Larissa"},
            {"name": "Salto", "address": "Rua Celso Odeli, 129, Salto", "field_id": 19, "shepherd": "Pb Jardel e Miss Bruna"},
            {"name": "Água Verde", "address": "Johann Ohf , 181 Água Verde", "field_id": 19, "shepherd": "Pb Gabriel e Miss Ana"},
            {"name": "Fortaleza", "address": "Rua Hermann Tribess, 583, Fortaleza 89055-400", "field_id": 19, "shepherd": "Pb Davi e Miss Amanda"},
            {"name": "Velha Grande", "address": "Rua Franz Muller, 1419 Velha Central, 89045-499", "field_id": 19, "shepherd": "Dc Vitor e Dc Cleide"},
            {"name": "Sede Rio Do Sul", "address": "Rua Osvaldo Hadlich, 94, Boa Vista", "field_id": 14, "shepherd": "Pr Anderson e Pra Mirian"},
            {"name": "Barragem", "address": "Estrada da Madeira,855, Barragem", "field_id": 14, "shepherd": "Miss Marli, Miss Gi e Dc Fernando"},
            {"name": "Lontras", "address": "Rua Willy Schroeder, 890, Centro, Lontras", "field_id": 14, "shepherd": "Miss Priscila"},
            {"name": "Monte Carlo", "address": "Rua Bernarino Lopes de Albuquerque,720", "field_id": 15, "shepherd": "Ev Pedro e Ev Thami"},
            {"name": "Campos Novos", "address": "SC 284, São José, Ibicuí", "field_id": 15, "shepherd": "Ev Pedro e Ev Thami"},
            {"name": "Três Rios do Norte", "address": "Rua Sizino Garcia,740 Três Rios do Norte", "field_id": 7, "shepherd": "Ev. Arilton e Ev Adriana"},
            {"name": "Sede Rau", "address": "Waldemar Ra, 710, Rau", "field_id": 7, "shepherd": "Ev Fabio e Ev Sueli"},
            {"name": "Tifa Martins", "address": "Rua Elpídio Rodrigues 84, Tifa Martins", "field_id": 7, "shepherd": "Pb Rafael e Miss Raquel"},
            {"name": "Jaraguá 99", "address": "Rua João Mass,352, Jaragua 99", "field_id": 7, "shepherd": "Miss Kelly, Dc André"},
            {"name": "Ilha da Figueira", "address": "José  Theodoro Ribeiro 4236, Ilha da Figueira", "field_id": 7, "shepherd": "Pb Leandro e Miss Jéssica"},
            {"name": "Rio da Luz", "address": "Ervino Rux s/n Rio da Luz", "field_id": 7, "shepherd": "Pb Leandro e Miss Jéssica"},
            {"name": "Corticeira", "address": "Rua Hermínio Stringari, 335, Corticeira, Guaramirim", "field_id": 7, "shepherd": "Miss Geslaine e Pb Eder"},
            {"name": "Avaí", "address": "Rua Ervino Hanemann, Avaí ,Guaramirim", "field_id": 7, "shepherd": "Pb Allan e Miss Flavia"},
            {"name": "Ribeirão Cavalo", "address": "Rua Ermelinda Trentini Menel, 300 , Ribeirão Cavalo, Jaragua", "field_id": 7, "shepherd": "Pb Aparecido e Miss Sara"},
            {"name": "Comassa", "address": "Rua João Ebert,1089, Comassa, Joinville", "field_id": 22, "shepherd": "Pr Moisés e Pra Sonia"},
            {"name": "Rio Bonito", "address": "Rua Quinze de Outubro,3570, Rio Bonito,", "field_id": 22, "shepherd": "Pb Ricardo e Miss Carla"},
            {"name": "Itinga", "address": "Rua Barra Velha, 276, Itinga, Araquari", "field_id": 22, "shepherd": "Pr Neri e Pra Rose"},
            {"name": "Sede", "address": None, "field_id": 8, "shepherd": "Pr Alex e Pra Grazi"},
            {"name": "São José", "address": None, "field_id": 8, "shepherd": "Pb Julci e Miss Leontina"},
            {"name": "Madre", "address": None, "field_id": 8, "shepherd": "Pb Rodinei e Miss Ritiane"},
            {"name": "Santa Terezinha do Itaipu", "address": "Rua das Acácias,2978, Santa Mônica, Santa Terezinha do Itapu", "field_id": 13, "shepherd": "Pr Romulo e Pra Rafa"},
            {"name": "Foz do Iguaçu", "address": "Av. Mané Garrincha, 2147,Parque Residencial Morumbi 2", "field_id": 13, "shepherd": "Pr Romulo e Pra Rafa"},
            {"name": "Sede", "address": "Rua Brasília,620, Centro, Dr Pedrinho", "field_id": 18, "shepherd": "Pb Andeson e Miss Rafa"},
            {"name": "Rodeio", "address": "Rua Aristides Pasqualine,66, Gávea, Rodeio", "field_id": 18, "shepherd": "Pr Oscar e Pra Isabela"},
            {"name": "Salto Donner", "address": "Rua da Glória, 838, Salto Donner, Dr Pedrinho", "field_id": 18, "shepherd": "Pb Nildo e Miss Amanda"},
            {"name": "Santa Maria", "address": "Rua Estrada Geral, Benedito Novo, 575, Santa Maria", "field_id": 18, "shepherd": "Pb Renan e Miss Sueli"},
            {"name": "Sede Porto União", "address": "Rua José Lona,705, Santa Rosa, Porto União", "field_id": 2, "shepherd": "Pr Rodrigo e Pra Bruna"},
            {"name": "Sede Mundo Novo", "address": "Rua Mundo Novo, Taquara", "field_id": 12, "shepherd": "Pr Anderson e Pra Cris"},
            {"name": "Gravataí", "address": None, "field_id": 12, "shepherd": "Pr Darlan e Pra Gabi"},
            {"name": "Empresa", "address": None, "field_id": 12, "shepherd": "Pb Henrique e Miss Rubia"},
            {"name": "Santo Antonio da Patrulha", "address": None, "field_id": 12, "shepherd": "Miss Letícia e Miss Lisiane"},
            {"name": "Mariscal", "address": "Rua Lourival de Souza 842, Mariscal, Penha", "field_id": 20, "shepherd": "Pb Gabriel e Miss Katlin"},
            {"name": "Centro Penha", "address": "Rua Duque de Caixas, 392, Centro", "field_id": 20, "shepherd": "Pb Gabriel e Miss Katlin"},
            {"name": "Sede Vista Alegre", "address": "Jorge Rueckl 1139, Vista Alegre", "field_id": 17, "shepherd": "Ev Alex e Ev Ariane"},
            {"name": "Cruzeiro", "address": "Adolfo Olsen 1185 Cruzeiro Rio Negrinho", "field_id": 17, "shepherd": "Ev Alex e Ev Ariane"},
            {"name": "Lageado", "address": "Ponte Divisa de Rio Negrinho", "field_id": 17, "shepherd": "Pb Luiz e Miss Leandra"},
            {"name": "São Pedro", "address": "Rua João da Rosa,46,São Pedro Rio Negrinho", "field_id": 17, "shepherd": "Pb Marcos e Miss Pamela"},
            {"name": "Cohab", "address": "Ruth Wtollmonn, 111, Industrial Norte", "field_id": 17, "shepherd": "Pb Nelson"},
            {"name": "Paulo Frontin", "address": "Rua 22 de Janeiro,132 , Centro, Paulo Frontin", "field_id": 2, "shepherd": "Ev Charles e Pra Patricia"},
            {"name": "São Gabriel", "address": "Laurindo Furlan, 97 Sao Gabriel, Porto União", "field_id": 2, "shepherd": "Pb Marcos e Miss Marcia"},
            {"name": "Irineopolis", "address": None, "field_id": 2, "shepherd": "Ev Roberto e Ev Debora"},
            {"name": "Vici King", "address": None, "field_id": 2, "shepherd": "Miss Amanda"},
            {"name": "Conjunto Porto União", "address": "Rua Brigadeiro Eduardo Gomes, 142 Conjunto Porto Uniao", "field_id": 2, "shepherd": "Dc Lisandro e Dc Rose"},
            {"name": "Bela Vista", "address": None, "field_id": 2, "shepherd": "Pb Jeferson e Miss Sheila"},
            {"name": "Candinha", "address": "Rua Pará, 711 Bairro Sra Aparecida, Irineópolis", "field_id": 2, "shepherd": "Pb Jucelino e Miss Elisangela"},
            {"name": "Rio das Antas", "address": None, "field_id": 6, "shepherd": "Pb Altamir e Ev Damiana"},
            {"name": "Rodeio Grande", "address": None, "field_id": 6, "shepherd": "Pb Altamir e Ev Damiana"},
            {"name": "Sede", "address": None, "field_id": 6, "shepherd": "Pr Junior e Pra Daiane"},
            {"name": "Lucena", "address": None, "field_id": 6, "shepherd": "Pb Carlos e Miss Bruna"},
            {"name": "Vila Nova", "address": None, "field_id": 6, "shepherd": "Pr João E Pra Risolete"},
            {"name": "Centro Papanduva", "address": "Papanduva", "field_id": 6, "shepherd": "Pb Christian e Miss Bruna"},
            {"name": "Major Vieira", "address": None, "field_id": 6, "shepherd": "Pb Moisés e Miss Jaqueline"},
            {"name": "Bom Jesus", "address": None, "field_id": 6, "shepherd": "Dc Elias e Dc Fabiele"},
            {"name": "Ulysses", "address": "Rua Nara Leão,831, Ulysses Guimarães, Joinville", "field_id": 22, "shepherd": "Ev Dione e Ev Renata"},
            {"name": "Jardim Paraíso", "address": "Rua Capriconius,231 Jardim Paraíso, Joinville", "field_id": 22, "shepherd": "Ev Sandro e Ev Marcelina"},
            {"name": "Canto do Rio", "address": "Avenida Urano, 154 , Canto do Rio, Joinville", "field_id": 22, "shepherd": "Pb Marcos e Miss Erica"},
            {"name": "Vila Paranaense", "address": "Max Boehm, 175, Vila Paranaense Joinville", "field_id": 22, "shepherd": "Dc Samuel e Pra Lilia"},
            {"name": "Industrial 1", "address": "Álvaro Soares Machado 1115, Industrial 1, Canoinhas", "field_id": 1, "shepherd": "Miss Luana e Miss Luana"},
            {"name": "Vila Nova", "address": "Rua Jaime Pinto Ribeiro,827, Vila Nova,São Mateus do Sul", "field_id": 1, "shepherd": "Pb Vosnei e Miss Tangriane"},
            {"name": "Joao Paulo", "address": "Rua Francisco Becker,140 João Paulo, Tres Barras", "field_id": 24, "shepherd": "Pb Gerson e Miss Rayane"},
            {"name": "Água verde", "address": "Rua Antonio Grosskopf,305 Água verde Canoinhas", "field_id": 1, "shepherd": "Pb Celio e Miss Renata"},
            {"name": "Piedade", "address": "Rua Emídio Ferreira,59, Piedade, Canoinhas", "field_id": 1, "shepherd": "Ev Danrlei e Ev Josi"},
            {"name": "São Cristovão", "address": "Rua Senador Leonir Vargas Ferreira,272,São Cristovão Três Barras", "field_id": 24, "shepherd": "Pb Gerson e Miss Rayane"},
            {"name": "Jardim Santa Cruz", "address": "Rua Francisco Celso de Paula  e Silva,32, São Mateus do Sul", "field_id": 1, "shepherd": "Pb Jocimar  e Miss Jheniffer"},
            {"name": "Jardim Esperança", "address": "Rua Walmor Ivo Gallote, 726, Jardim Esperança,  Canoinhas", "field_id": 1, "shepherd": "Ev Adilson e Miss Márcia"},
            {"name": "Bela Vista", "address": "Rua Professor Alfredo Ludka,109, Bela Vista, Canoinhas", "field_id": 1, "shepherd": "Ev Adilson e Miss Márcia"},
            {"name": "Marcilio Dias", "address": "Rua Germano Raabe, 277, Marcilio Dias , Três Barras", "field_id": 24, "shepherd": "Pb Gilberto e Miss Josiane"},
            {"name": "Alto da Tijuca", "address": "Rua Bernado Olsen,251, Alto da Tijuca,  Canoinhas", "field_id": 1, "shepherd": "Dc Luiz e Miss Dirlene"},
            {"name": "Tamareiras", "address": "Rua Damázio Ferreira Mayer 262, São Mateus do Sul", "field_id": 1, "shepherd": "Pb Adriano e Miss Li"},
            {"name": "Fátima", "address": "Rua Guanabara, Fatima Joinville", "field_id": 24, "shepherd": "Pr Neri e Pra Rose"},
            {"name": "Caixa Geral", "address": "Joinville", "field_id": 23, "shepherd": "Pastora Bruna"},
            {"name": "Amola Flecha", "address": "Vital Brasil, Amola Flecha,", "field_id": 5, "shepherd": "Pb Willian e Miss Aline"},
            {"name": "Vila Ivete", "address": None, "field_id": 5, "shepherd": "Pb Maicon e Miss Thaciane"},
            {"name": "Vila Nova", "address": None, "field_id": 5, "shepherd": "Pb Evaristo e Miss Rosangela"},
            {"name": "Km 9", "address": None, "field_id": 5, "shepherd": "Pb Antonio e  Miss Jaciara"},
            {"name": "Campo do Tenente", "address": None, "field_id": 5, "shepherd": "Ev Claudio  e Ev Rosani"},
            {"name": "Rio Negro", "address": "Rio Negro", "field_id": 5, "shepherd": "Pr Odair e Ev Cristina"},
            {"name": "Sede Itajaí", "address": None, "field_id": 9, "shepherd": "Pr Welinton e Pra Emilaine"},
            {"name": "Camboriú", "address": None, "field_id": 11, "shepherd": "Pb Juliano e Miss Luciana"},
            {"name": "Pontal", "address": None, "field_id": 10, "shepherd": "Pb Erinton e Miss Tainã"},
            {"name": "São Paulo", "address": None, "field_id": 10, "shepherd": "Pb Marcos e Miss Debora"},
            {"name": "Meia Praia", "address": None, "field_id": 10, "shepherd": "Pb Marcos e Miss Debora"},
            {"name": "São Domingos", "address": None, "field_id": 10, "shepherd": "Miss Mônica"},
            {"name": "Sede Barra Velha", "address": "Rua Manoel Correa,916, São Cristóvão, Barra Velha", "field_id": 21, "shepherd": "Pr Douglas e Ev Lirian"},
            {"name": "Vila Nova", "address": None, "field_id": 21, "shepherd": "Pb Marcos e Miss  Joci"},
            {"name": "Itajuba I", "address": None, "field_id": 21, "shepherd": "Pra Paula"},
            {"name": "Poeirão", "address": None, "field_id": 21, "shepherd": "Miss Elenir"}
        ]

        # Criar pastores e igrejas
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('⛪ Criando pastores e igrejas...')
        )
        self.stdout.write('='*50)

        # Extrair pastores únicos das igrejas
        unique_shepherds = set()
        for church_data in churches_data:
            unique_shepherds.add(church_data['shepherd'])

        # Criar pastores
        shepherds_created_count = 0
        shepherds_skipped_count = 0
        shepherd_map = {}  # Mapear nome do pastor para objeto Shepherd

        for shepherd_name in sorted(unique_shepherds):
            shepherd, created = Shepherd.objects.get_or_create(
                name=shepherd_name
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Pastor criado: {shepherd_name}')
                )
                shepherds_created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'⏭️  Pastor pulado (já existe): {shepherd_name}')
                )
                shepherds_skipped_count += 1
            
            shepherd_map[shepherd_name] = shepherd

        # Criar igrejas
        churches_created_count = 0
        churches_skipped_count = 0

        for church_data in churches_data:
            name = church_data['name']
            address = church_data['address']
            field_id = church_data['field_id']
            shepherd_name = church_data['shepherd']

            try:
                field = Field.objects.get(id=field_id)
                shepherd = shepherd_map[shepherd_name]
                
                # Verificar se a igreja já existe
                church, created = Church.objects.get_or_create(
                    name=name,
                    field=field,
                    defaults={
                        'address': address,
                        'shepherd': shepherd,
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Igreja criada: {name} - {field.name} - {shepherd_name}')
                    )
                    churches_created_count += 1
                else:
                    if options['force']:
                        # Atualizar igreja existente
                        church.address = address
                        church.shepherd = shepherd
                        church.save()
                        self.stdout.write(
                            self.style.WARNING(f'🔄 Igreja atualizada: {name} - {field.name} - {shepherd_name}')
                        )
                        churches_created_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⏭️  Igreja pulada (já existe): {name} - {field.name} - {shepherd_name}')
                        )
                        churches_skipped_count += 1
                        
            except Field.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Campo não encontrado: ID {field_id} para igreja {name}')
                )

        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'📊 RESUMO FINAL:')
        )
        self.stdout.write('='*50)
        
        # Resumo dos campos
        self.stdout.write(
            self.style.SUCCESS(f'🏗️  CAMPOS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criados: {fields_created_count}')
        )
        if options['force']:
            self.stdout.write(
                self.style.WARNING(f'   🔄 Atualizados: {fields_updated_count}')
            )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Pulados: {fields_skipped_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📈 Total de campos no sistema: {Field.objects.count()}')
        )
        
        # Resumo das categorias
        self.stdout.write(
            self.style.SUCCESS(f'🏷️  CATEGORIAS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criadas: {created_count}')
        )
        if options['force']:
            self.stdout.write(
                self.style.WARNING(f'   🔄 Atualizadas: {updated_count}')
            )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Puladas: {skipped_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📈 Total de categorias no sistema: {Category.objects.count()}')
        )
        
        # Resumo dos usuários
        self.stdout.write(
            self.style.SUCCESS(f'👥 USUÁRIOS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criados: {users_created_count}')
        )
        if options['force']:
            self.stdout.write(
                self.style.WARNING(f'   🔄 Atualizados: {users_updated_count}')
            )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Pulados: {users_skipped_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📈 Total de usuários no sistema: {User.objects.count()}')
        )
        
        # Resumo das atribuições de campos
        self.stdout.write(
            self.style.SUCCESS(f'🔗 ATRIBUIÇÕES DE CAMPOS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criadas: {user_fields_created_count}')
        )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Puladas: {user_fields_skipped_count}')
        )
        
        # Resumo dos pastores
        self.stdout.write(
            self.style.SUCCESS(f'👨‍💼 PASTORES:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criados: {shepherds_created_count}')
        )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Pulados: {shepherds_skipped_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📈 Total de pastores no sistema: {Shepherd.objects.count()}')
        )
        
        # Resumo das igrejas
        self.stdout.write(
            self.style.SUCCESS(f'⛪ IGREJAS:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Criadas: {churches_created_count}')
        )
        self.stdout.write(
            self.style.WARNING(f'   ⏭️  Puladas: {churches_skipped_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📈 Total de igrejas no sistema: {Church.objects.count()}')
        )
        self.stdout.write('='*50)

        total_created = fields_created_count + created_count + users_created_count + user_fields_created_count + shepherds_created_count + churches_created_count
        total_updated = fields_updated_count + updated_count + users_updated_count
        
        if total_created > 0 or (options['force'] and total_updated > 0):
            self.stdout.write(
                self.style.SUCCESS('🎉 Dados iniciais criados com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Nenhum novo dado foi criado.')
            )
