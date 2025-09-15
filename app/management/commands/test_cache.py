from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'Testar configuração do Redis Cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['basic', 'performance', 'session', 'all'],
            default='basic',
            help='Tipo de teste a executar'
        )

    def handle(self, *args, **options):
        test_type = options['test_type']
        
        if test_type in ['basic', 'all']:
            self.test_basic_cache()
        
        if test_type in ['performance', 'all']:
            self.test_performance()
        
        if test_type in ['session', 'all']:
            self.test_session_cache()
        
        if test_type == 'all':
            self.test_cache_cleanup()

    def test_basic_cache(self):
        """Teste básico de cache"""
        self.stdout.write('🧪 Testando cache básico...')
        
        # Teste de escrita e leitura
        test_key = 'test_basic_cache'
        test_value = {'message': 'Hello Redis!', 'timestamp': timezone.now().isoformat()}
        
        # Escrever no cache
        cache.set(test_key, test_value, 60)
        self.stdout.write('✅ Dados escritos no cache')
        
        # Ler do cache
        cached_value = cache.get(test_key)
        if cached_value == test_value:
            self.stdout.write('✅ Dados lidos do cache corretamente')
        else:
            self.stdout.write('❌ Erro na leitura do cache')
        
        # Teste de TTL
        cache.set('test_ttl', 'expires_soon', 2)
        time.sleep(3)
        if cache.get('test_ttl') is None:
            self.stdout.write('✅ TTL funcionando corretamente')
        else:
            self.stdout.write('❌ TTL não funcionou')
        
        # Limpeza
        cache.delete(test_key)
        self.stdout.write('✅ Cache básico funcionando!')

    def test_performance(self):
        """Teste de performance do cache"""
        self.stdout.write('🚀 Testando performance do cache...')
        
        # Teste de escrita em lote
        start_time = time.time()
        test_data = {}
        
        for i in range(100):
            test_data[f'perf_test_{i}'] = {
                'id': i,
                'data': f'Test data {i}',
                'timestamp': timezone.now().isoformat()
            }
        
        # Escrever em lote
        cache.set_many(test_data, 300)
        write_time = time.time() - start_time
        
        # Teste de leitura em lote
        start_time = time.time()
        keys = list(test_data.keys())
        cached_data = cache.get_many(keys)
        read_time = time.time() - start_time
        
        self.stdout.write(f'✅ Escrita de 100 itens: {write_time:.3f}s')
        self.stdout.write(f'✅ Leitura de 100 itens: {read_time:.3f}s')
        
        # Limpeza
        cache.delete_many(keys)
        self.stdout.write('✅ Teste de performance concluído!')

    def test_session_cache(self):
        """Teste de cache de sessão"""
        self.stdout.write('👤 Testando cache de sessão...')
        
        # Simular dados de sessão
        session_data = {
            'user_id': 123,
            'username': 'testuser',
            'permissions': ['read', 'write'],
            'last_activity': timezone.now().isoformat()
        }
        
        session_key = 'session_test_123'
        cache.set(session_key, session_data, 3600)
        
        # Verificar se os dados estão no cache
        cached_session = cache.get(session_key)
        if cached_session and cached_session['user_id'] == 123:
            self.stdout.write('✅ Cache de sessão funcionando')
        else:
            self.stdout.write('❌ Erro no cache de sessão')
        
        # Limpeza
        cache.delete(session_key)
        self.stdout.write('✅ Teste de sessão concluído!')

    def test_cache_cleanup(self):
        """Teste de limpeza do cache"""
        self.stdout.write('🧹 Testando limpeza do cache...')
        
        # Adicionar alguns dados de teste
        test_keys = []
        for i in range(10):
            key = f'cleanup_test_{i}'
            cache.set(key, f'data_{i}', 300)
            test_keys.append(key)
        
        # Verificar se estão no cache
        cached_data = cache.get_many(test_keys)
        if len(cached_data) == 10:
            self.stdout.write('✅ Dados de teste adicionados')
        
        # Limpar cache
        cache.clear()
        
        # Verificar se foram removidos
        cached_data = cache.get_many(test_keys)
        if len(cached_data) == 0:
            self.stdout.write('✅ Cache limpo com sucesso')
        else:
            self.stdout.write('❌ Erro na limpeza do cache')
        
        self.stdout.write('✅ Teste de limpeza concluído!')

    def test_redis_info(self):
        """Mostrar informações do Redis"""
        self.stdout.write('📊 Informações do Redis:')
        
        try:
            # Informações básicas do Redis
            info = cache._cache.get_client().info()
            
            self.stdout.write(f'  Versão: {info.get("redis_version", "N/A")}')
            self.stdout.write(f'  Uptime: {info.get("uptime_in_seconds", 0)} segundos')
            self.stdout.write(f'  Memória usada: {info.get("used_memory_human", "N/A")}')
            self.stdout.write(f'  Conexões: {info.get("connected_clients", 0)}')
            self.stdout.write(f'  Chaves expiradas: {info.get("expired_keys", 0)}')
            
        except Exception as e:
            self.stdout.write(f'❌ Erro ao obter informações: {e}')
