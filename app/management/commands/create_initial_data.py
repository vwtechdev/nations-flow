from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app.models import Field, User


class Command(BaseCommand):
    help = 'Cria dados iniciais do sistema: usuários administradores, tesoureiros e campos'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando criação dos dados iniciais...')
        
        # 1. Criar campos
        self.create_fields()
        
        # 2. Criar usuários administradores
        self.create_administrators()
        
        # 3. Criar usuários tesoureiros
        self.create_treasurers()
        
        self.stdout.write(self.style.SUCCESS('✅ Dados iniciais criados com sucesso!'))

    def create_fields(self):
        """Cria todos os campos necessários"""
        self.stdout.write('📍 Criando campos...')
        
        fields_data = [
            # Campos existentes
            'Canoinhas', 'Porto União', 'São Paulo', 'Curitiba', 'Mafra', 'Itaiopolis',
            'Jaraguá do Sul', 'São Joaquim', 'Itajaí', 'Navegantes', 'Camburiú',
            'Rio Grande do Sul', 'Foz do Iguaçu', 'Rio do Sul', 'Campos Novos',
            'São Bento do Sul', 'Rio Negrinho', 'Doutor Pedrinho', 'Blumenal', 'Penha',
            # Novos campos
            'Barra Velha', 'Joinville'
        ]
        
        created_fields = []
        for field_name in fields_data:
            field, created = Field.objects.get_or_create(name=field_name)
            if created:
                self.stdout.write(f'  ✅ Campo criado: {field_name}')
            else:
                self.stdout.write(f'  ℹ️  Campo já existe: {field_name}')
            created_fields.append(field)
        
        self.stdout.write(f'  📊 Total de campos: {len(created_fields)}')
        return created_fields

    def create_administrators(self):
        """Cria usuários administradores"""
        self.stdout.write('👑 Criando usuários administradores...')
        
        administrators_data = [
            {
                'first_name': 'Bruna',
                'last_name': 'dos Santos Colaço',
                'email': 'Israelbruna0@gmail.com',
                'username': 'bruna.colaco'
            },
            {
                'first_name': 'Lirian',
                'last_name': 'Nara Floriano de Lima',
                'email': 'Lirian.floriano2018@gmail.com',
                'username': 'lirian.floriano'
            }
        ]
        
        for admin_data in administrators_data:
            user, created = User.objects.get_or_create(
                email=admin_data['email'],
                defaults={
                    'username': admin_data['username'],
                    'first_name': admin_data['first_name'],
                    'last_name': admin_data['last_name'],
                    'role': 'admin',
                    'password': make_password('nations123456'),
                    'password_changed': False,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Administrador criado: {admin_data["first_name"]} {admin_data["last_name"]}')
            else:
                self.stdout.write(f'  ℹ️  Administrador já existe: {admin_data["first_name"]} {admin_data["last_name"]}')

    def create_treasurers(self):
        """Cria usuários tesoureiros"""
        self.stdout.write('💰 Criando usuários tesoureiros...')
        
        treasurers_data = [
            {
                'first_name': 'Jamille',
                'last_name': 'Santos Bahia Costa',
                'email': 'eventosnacoesscanoinhas@gmail.com',
                'username': 'jamille.costa',
                'fields': ['Canoinhas', 'Porto União']
            },
            {
                'first_name': 'Marco',
                'last_name': 'Antonio do Nascimento',
                'email': 'marconascimento381@gmail.com',
                'username': 'marco.nascimento',
                'fields': ['São Paulo', 'Curitiba']
            },
            {
                'first_name': 'Tatiane',
                'last_name': 'Micheli de Andrade Andruchechen',
                'email': 'tatiiane.andrade@gmail.com',
                'username': 'tatiane.andrade',
                'fields': ['Mafra', 'Itaiopolis']
            },
            {
                'first_name': 'Fátima',
                'last_name': 'Silva Macalli',
                'email': 'fatimaevangelista.nacoes@gmail.com',
                'username': 'fatima.macalli',
                'fields': ['Jaraguá do Sul']
            },
            {
                'first_name': 'Katlin',
                'last_name': 'Caroline da Silva Lemos',
                'email': 'tesourariakatlin@gmail.com',
                'username': 'katlin.lemos',
                'fields': ['São Joaquim']
            },
            {
                'first_name': 'Marilia',
                'last_name': 'Elizabete Teixeira da Silva',
                'email': 'mariliaelizabeti.23@gmail.com',
                'username': 'marilia.silva',
                'fields': ['Itajaí', 'Navegantes', 'Camburiú']
            },
            {
                'first_name': 'Cristina',
                'last_name': 'Veiga Bueno',
                'email': 'cristinaveiga025@gmail.com',
                'username': 'cristina.bueno',
                'fields': ['Rio Grande do Sul']
            },
            {
                'first_name': 'Rafaela',
                'last_name': 'Cristine Neuber',
                'email': 'rafaelaneuber@gmail.com',
                'username': 'rafaela.neuber',
                'fields': ['Foz do Iguaçu']
            },
            {
                'first_name': 'Mirian',
                'last_name': 'Silva Budal Floriano',
                'email': 'mirianfamilia84@gmail.com',
                'username': 'mirian.floriano',
                'fields': ['Rio do Sul', 'Campos Novos']
            },
            {
                'first_name': 'Ricardo',
                'last_name': 'Silva de Oliveira',
                'email': 'Ricardoadri.oliveira@gmail.com',
                'username': 'ricardo.oliveira',
                'fields': ['São Bento do Sul', 'Rio Negrinho']
            },
            {
                'first_name': 'Crislaine',
                'last_name': 'de Oliveira',
                'email': 'crislainecris0107@outlook.com',
                'username': 'crislaine.oliveira',
                'fields': ['Doutor Pedrinho']
            },
            {
                'first_name': 'Ana Cláudia',
                'last_name': 'Fleit dos Santos',
                'email': 'annafleit200@gmail.com',
                'username': 'ana.fleit',
                'fields': ['Porto União']
            },
            {
                'first_name': 'Matheus',
                'last_name': 'Anderle',
                'email': 'matheus.anderle@hotmail.com',
                'username': 'matheus.anderle',
                'fields': ['Blumenal']
            },
            {
                'first_name': 'Nayara',
                'last_name': 'de Oliveira Brito',
                'email': 'nayarabr691@gmail.com',
                'username': 'nayara.brito',
                'fields': ['Penha']
            }
        ]
        
        for treasurer_data in treasurers_data:
            # Criar ou obter o usuário
            user, created = User.objects.get_or_create(
                email=treasurer_data['email'],
                defaults={
                    'username': treasurer_data['username'],
                    'first_name': treasurer_data['first_name'],
                    'last_name': treasurer_data['last_name'],
                    'role': 'treasurer',
                    'password': make_password('nations123456'),
                    'password_changed': False,
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Tesoureiro criado: {treasurer_data["first_name"]} {treasurer_data["last_name"]}')
            else:
                self.stdout.write(f'  ℹ️  Tesoureiro já existe: {treasurer_data["first_name"]} {treasurer_data["last_name"]}')
            
            # Associar campos ao usuário
            fields_to_add = []
            for field_name in treasurer_data['fields']:
                try:
                    field = Field.objects.get(name=field_name)
                    fields_to_add.append(field)
                except Field.DoesNotExist:
                    self.stdout.write(f'    ⚠️  Campo não encontrado: {field_name}')
            
            # Adicionar campos ao usuário
            if fields_to_add:
                user.fields.add(*fields_to_add)
                field_names = [f.name for f in fields_to_add]
                self.stdout.write(f'    🔗 Campos associados: {", ".join(field_names)}')
            else:
                self.stdout.write(f'    ⚠️  Nenhum campo foi associado ao usuário')
        
        self.stdout.write(f'  📊 Total de tesoureiros processados: {len(treasurers_data)}')
