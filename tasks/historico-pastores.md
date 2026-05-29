# Implementação: Histórico e Informações Completas de Pastores

## Visão Geral

Esta tarefa implementa um sistema completo de gestão de informações de pastores, incluindo histórico de atuação em igrejas, contratos, endereço e informações familiares. Isso permitirá rastrear o histórico completo de cada pastor ao longo do tempo.

## Objetivo

Expandir o modelo `Shepherd` para incluir:
1. **Histórico de Atuação**: Rastrear entrada e saída de pastores em cada igreja com períodos específicos
2. **Contrato**: Anexo de documentos contratuais
3. **Endereço**: Informações de endereço do pastor
4. **Familiares**: Cadastro de familiares (nome e idade)

## Funcionalidades Principais

### 1. Histórico de Atuação em Igrejas
- Registrar data de entrada do pastor em uma igreja
- Registrar data de saída do pastor de uma igreja
- Visualizar histórico completo de todas as igrejas onde o pastor atuou
- Filtrar transações por período de atuação do pastor
- Relatórios de período de atuação

### 2. Contrato
- Upload de arquivo de contrato (PDF, DOC, DOCX)
- Visualização de contratos
- Download de contratos
- Validação de formato e tamanho

### 3. Endereço
- Endereço completo do pastor
- CEP, cidade, estado
- Complemento (opcional)

### 4. Familiares
- Cadastro de familiares (cônjuge, filhos, etc.)
- Nome e idade de cada familiar
- Relacionamento com o pastor (opcional)

## Modelos de Dados

### 1. Modificação do Modelo Shepherd

**Arquivo:** `app/models.py`

**Campos a adicionar:**
```python
class Shepherd(models.Model):
    # Campos existentes
    name = models.CharField(max_length=200, verbose_name="Nome do Pastor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # NOVOS CAMPOS
    address = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    state = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    address_complement = models.CharField(max_length=200, blank=True, null=True, verbose_name="Complemento")
    contract = models.FileField(
        upload_to='contracts/pastors/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Contrato",
        help_text="Formatos aceitos: PDF, DOC, DOCX. Tamanho máximo: 5MB"
    )
    
    class Meta:
        verbose_name = "Pastor"
        verbose_name_plural = "Pastores"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name
    
    def get_full_address(self):
        """Retorna endereço completo formatado"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.address_complement:
            parts.append(self.address_complement)
        if self.cep:
            parts.append(f"CEP: {self.cep}")
        if self.city and self.state:
            parts.append(f"{self.city}/{self.state}")
        return ", ".join(parts) if parts else "Não informado"
```

### 2. Novo Modelo: ShepherdHistory

**Arquivo:** `app/models.py`

**Modelo para histórico de atuação:**
```python
class ShepherdHistory(models.Model):
    """Histórico de atuação de pastores em igrejas"""
    shepherd = models.ForeignKey(
        Shepherd,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Pastor"
    )
    church = models.ForeignKey(
        Church,
        on_delete=models.CASCADE,
        related_name='shepherd_history',
        verbose_name="Igreja"
    )
    start_date = models.DateField(verbose_name="Data de Entrada")
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Saída",
        help_text="Deixe em branco se ainda está atuando"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se o pastor ainda está atuando nesta igreja"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Histórico de Pastor"
        verbose_name_plural = "Históricos de Pastores"
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['shepherd', 'start_date']),
            models.Index(fields=['church', 'start_date']),
        ]
    
    def __str__(self):
        status = "Ativo" if self.is_active else "Inativo"
        return f"{self.shepherd.name} - {self.church.name} ({self.start_date} até {self.end_date or 'atual'}) - {status}"
    
    def clean(self):
        """Validações"""
        from django.core.exceptions import ValidationError
        
        # Data de saída deve ser posterior à data de entrada
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'Data de saída deve ser posterior à data de entrada.'
                })
        
        # Se end_date está preenchido, is_active deve ser False
        if self.end_date:
            self.is_active = False
        else:
            self.is_active = True
    
    def get_duration_days(self):
        """Retorna duração em dias"""
        if not self.end_date:
            from datetime import date
            end = date.today()
        else:
            end = self.end_date
        return (end - self.start_date).days
    
    def get_duration_months(self):
        """Retorna duração aproximada em meses"""
        from dateutil.relativedelta import relativedelta
        if not self.end_date:
            from datetime import date
            end = date.today()
        else:
            end = self.end_date
        delta = relativedelta(end, self.start_date)
        return delta.years * 12 + delta.months
```

### 3. Novo Modelo: ShepherdFamily

**Arquivo:** `app/models.py`

**Modelo para familiares:**
```python
class ShepherdFamily(models.Model):
    """Familiares do pastor"""
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Cônjuge'),
        ('son', 'Filho(a)'),
        ('daughter', 'Filha'),
        ('father', 'Pai'),
        ('mother', 'Mãe'),
        ('brother', 'Irmão(ã)'),
        ('other', 'Outro'),
    ]
    
    shepherd = models.ForeignKey(
        Shepherd,
        on_delete=models.CASCADE,
        related_name='family',
        verbose_name="Pastor"
    )
    name = models.CharField(max_length=200, verbose_name="Nome")
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Idade",
        help_text="Idade atual ou idade no momento do cadastro"
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Nascimento",
        help_text="Alternativa à idade. Se preenchida, a idade será calculada automaticamente"
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='other',
        verbose_name="Relacionamento"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Familiar do Pastor"
        verbose_name_plural = "Familiares dos Pastores"
        ordering = ['relationship', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) - {self.shepherd.name}"
    
    def get_current_age(self):
        """Calcula idade atual baseada na data de nascimento"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return self.age
    
    def clean(self):
        """Validações"""
        from django.core.exceptions import ValidationError
        
        # Pelo menos idade ou data de nascimento deve ser informada
        if not self.age and not self.birth_date:
            raise ValidationError({
                'age': 'Informe a idade ou a data de nascimento.',
                'birth_date': 'Informe a idade ou a data de nascimento.'
            })
```

## Modificação do Modelo Church

**Arquivo:** `app/models.py`

**Mudança no relacionamento:**
- O relacionamento atual `Church.shepherd` (ForeignKey) deve ser mantido para compatibilidade
- O histórico será gerenciado através do modelo `ShepherdHistory`
- Considerar adicionar método helper para obter pastor ativo:

```python
class Church(models.Model):
    # ... campos existentes ...
    shepherd = models.ForeignKey(Shepherd, on_delete=models.CASCADE, verbose_name="Pastor Responsável")
    
    def get_active_shepherd_history(self):
        """Retorna o histórico ativo do pastor nesta igreja"""
        return self.shepherd_history.filter(is_active=True).first()
    
    def get_current_shepherd(self):
        """Retorna o pastor atual (via histórico ou relacionamento direto)"""
        history = self.get_active_shepherd_history()
        if history:
            return history.shepherd
        return self.shepherd  # Fallback para relacionamento direto
```

## Formulários

### 1. ShepherdForm - Atualizado

**Arquivo:** `app/forms.py`

**Campos a adicionar:**
```python
class ShepherdForm(forms.ModelForm):
    class Meta:
        model = Shepherd
        fields = [
            'name',
            'address',
            'cep',
            'city',
            'state',
            'address_complement',
            'contract'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),  # Com estados brasileiros
            'address_complement': forms.TextInput(attrs={'class': 'form-control'}),
            'contract': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }
    
    def clean_contract(self):
        contract = self.cleaned_data.get('contract')
        if contract:
            # Validar tamanho (5MB)
            if contract.size > 5 * 1024 * 1024:
                raise forms.ValidationError('O arquivo deve ter no máximo 5MB.')
            
            # Validar extensão
            valid_extensions = ['.pdf', '.doc', '.docx']
            ext = os.path.splitext(contract.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Formato inválido. Use PDF, DOC ou DOCX.')
        
        return contract
```

### 2. Novo Formulário: ShepherdHistoryForm

**Arquivo:** `app/forms.py`

```python
class ShepherdHistoryForm(forms.ModelForm):
    class Meta:
        model = ShepherdHistory
        fields = ['shepherd', 'church', 'start_date', 'end_date', 'notes', 'is_active']
        widgets = {
            'shepherd': forms.Select(attrs={'class': 'form-control'}),
            'church': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_active = cleaned_data.get('is_active')
        
        if end_date and start_date:
            if end_date < start_date:
                raise forms.ValidationError({
                    'end_date': 'Data de saída deve ser posterior à data de entrada.'
                })
        
        # Se end_date está preenchido, is_active deve ser False
        if end_date:
            cleaned_data['is_active'] = False
        
        return cleaned_data
```

### 3. Novo Formulário: ShepherdFamilyForm

**Arquivo:** `app/forms.py`

```python
class ShepherdFamilyForm(forms.ModelForm):
    class Meta:
        model = ShepherdFamily
        fields = ['name', 'age', 'birth_date', 'relationship', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')
        birth_date = cleaned_data.get('birth_date')
        
        if not age and not birth_date:
            raise forms.ValidationError({
                'age': 'Informe a idade ou a data de nascimento.',
                'birth_date': 'Informe a idade ou a data de nascimento.'
            })
        
        return cleaned_data
```

## Views

### 1. Atualização das Views Existentes

**Arquivo:** `app/views.py`

**Views a modificar:**
- `shepherd_list()` - Adicionar informações de histórico
- `shepherd_edit()` - Incluir formulários de histórico e familiares
- `shepherd_create()` - Incluir campos novos

### 2. Novas Views

**Arquivo:** `app/views.py`

#### `shepherd_detail(request, pk)`
- Visualização completa do pastor
- Histórico de igrejas
- Lista de familiares
- Visualização de contrato

#### `shepherd_history_create(request, shepherd_pk)`
- Criar novo registro de histórico
- Validar datas e sobreposições

#### `shepherd_history_edit(request, pk)`
- Editar histórico existente
- Finalizar período (definir end_date)

#### `shepherd_family_create(request, shepherd_pk)`
- Adicionar familiar ao pastor

#### `shepherd_family_edit(request, pk)`
- Editar familiar

#### `shepherd_family_delete(request, pk)`
- Excluir familiar

#### `shepherd_contract_view(request, pk)`
- Visualizar contrato (PDF viewer ou download)

## Templates

### 1. shepherd_detail.html (NOVO)

**Estrutura:**
- Informações básicas do pastor
- Endereço completo
- Contrato (visualizar/download)
- Aba de Histórico (tabela com todas as igrejas)
- Aba de Familiares (lista de familiares)
- Botões de ação (editar, adicionar histórico, adicionar familiar)

### 2. shepherd_form.html (ATUALIZAR)

**Adicionar:**
- Campos de endereço
- Campo de upload de contrato
- Seção de familiares (inline forms)
- Preview do contrato atual (se existir)

### 3. shepherd_list.html (ATUALIZAR)

**Adicionar:**
- Coluna "Igreja Atual"
- Coluna "Período Atual" (data de entrada)
- Link para detalhes completos

### 4. shepherd_history_form.html (NOVO)

**Formulário para:**
- Selecionar pastor e igreja
- Data de entrada
- Data de saída (opcional)
- Observações

### 5. shepherd_family_form.html (NOVO)

**Formulário para:**
- Nome do familiar
- Idade ou data de nascimento
- Relacionamento
- Observações

## Funcionalidades de Filtro

### Filtro por Período de Atuação

**Modificar views de transações:**
- Adicionar filtro que considere o período de atuação do pastor
- Ao filtrar por pastor, considerar apenas transações no período em que ele atuou na igreja

**Exemplo:**
```python
# Em transaction_list ou transaction_list_api
if selected_shepherd:
    # Buscar histórico do pastor
    shepherd_histories = ShepherdHistory.objects.filter(
        shepherd_id=selected_shepherd,
        is_active=True
    )
    
    # Filtrar transações por igrejas e período
    church_ids = shepherd_histories.values_list('church_id', flat=True)
    transactions = transactions.filter(church_id__in=church_ids)
    
    # Filtrar por período se data especificada
    if date_from or date_to:
        # Considerar apenas períodos que se sobrepõem com o filtro de data
        # ...
```

## Migrações

### 1. Migração para Shepherd

**Arquivo:** `app/migrations/XXXX_add_shepherd_fields.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('app', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='shepherd',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Endereço Completo'),
        ),
        migrations.AddField(
            model_name='shepherd',
            name='cep',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='shepherd',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='shepherd',
            name='state',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='shepherd',
            name='address_complement',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Complemento'),
        ),
        migrations.AddField(
            model_name='shepherd',
            name='contract',
            field=models.FileField(blank=True, help_text='Formatos aceitos: PDF, DOC, DOCX. Tamanho máximo: 5MB', null=True, upload_to='contracts/pastors/%Y/%m/%d/', verbose_name='Contrato'),
        ),
    ]
```

### 2. Migração para ShepherdHistory

**Arquivo:** `app/migrations/XXXX_create_shepherd_history.py`

### 3. Migração para ShepherdFamily

**Arquivo:** `app/migrations/XXXX_create_shepherd_family.py`

## APIs

### 1. API de Histórico

**Endpoint:** `/api/shepherd/<pk>/history/`

**Retorno:**
```json
{
    "shepherd": {
        "id": 1,
        "name": "Pastor João"
    },
    "history": [
        {
            "id": 1,
            "church": {
                "id": 1,
                "name": "Igreja Central"
            },
            "start_date": "2020-01-15",
            "end_date": null,
            "is_active": true,
            "duration_days": 1234,
            "duration_months": 40
        }
    ]
}
```

### 2. API de Familiares

**Endpoint:** `/api/shepherd/<pk>/family/`

**Retorno:**
```json
{
    "shepherd": {
        "id": 1,
        "name": "Pastor João"
    },
    "family": [
        {
            "id": 1,
            "name": "Maria Silva",
            "age": 35,
            "relationship": "spouse",
            "relationship_display": "Cônjuge"
        }
    ]
}
```

## Validações e Regras de Negócio

### 1. Histórico
- Um pastor não pode ter dois períodos ativos simultâneos na mesma igreja
- Data de entrada não pode ser futura
- Data de saída deve ser posterior à data de entrada
- Ao criar novo histórico, finalizar histórico anterior se necessário

### 2. Contrato
- Tamanho máximo: 5MB
- Formatos aceitos: PDF, DOC, DOCX
- Validar extensão e tipo MIME

### 3. Familiares
- Pelo menos idade ou data de nascimento deve ser informada
- Se data de nascimento fornecida, calcular idade automaticamente

## Testes Necessários

### 1. Modelos
- [ ] Criar histórico de pastor
- [ ] Validar datas de entrada/saída
- [ ] Calcular duração corretamente
- [ ] Adicionar familiares
- [ ] Calcular idade a partir de data de nascimento

### 2. Formulários
- [ ] Validação de contrato (tamanho, formato)
- [ ] Validação de datas no histórico
- [ ] Validação de idade/data de nascimento

### 3. Views
- [ ] Visualizar detalhes do pastor
- [ ] Criar/editar histórico
- [ ] Criar/editar familiar
- [ ] Visualizar contrato
- [ ] Filtrar transações por período de atuação

### 4. Integração
- [ ] Histórico aparece na listagem
- [ ] Familiares aparecem no detalhe
- [ ] Contrato pode ser visualizado e baixado
- [ ] Filtros de transação consideram período de atuação

## Ordem de Implementação Sugerida

1. **Migrações**: Criar modelos ShepherdHistory e ShepherdFamily
2. **Modelos**: Implementar métodos helper e validações
3. **Formulários**: Criar formulários para histórico e familiares
4. **Views**: Implementar views de detalhe e CRUD
5. **Templates**: Criar templates para visualização
6. **APIs**: Criar endpoints para histórico e familiares
7. **Integração**: Integrar com filtros de transações
8. **Testes**: Testar todas as funcionalidades

## Arquivos a Criar/Modificar

### Novos Arquivos
- `app/migrations/XXXX_add_shepherd_fields.py`
- `app/migrations/XXXX_create_shepherd_history.py`
- `app/migrations/XXXX_create_shepherd_family.py`
- `app/templates/pages/shepherd_detail.html`
- `app/templates/pages/shepherd_history_form.html`
- `app/templates/pages/shepherd_family_form.html`

### Arquivos a Modificar
- `app/models.py` (adicionar campos e novos modelos)
- `app/forms.py` (atualizar ShepherdForm, adicionar novos formulários)
- `app/views.py` (atualizar views existentes, adicionar novas views)
- `app/urls.py` (adicionar novas rotas)
- `app/templates/pages/shepherd_list.html`
- `app/templates/pages/shepherd_form.html`

## Considerações de UX

### 1. Interface
- Usar abas para organizar informações (Básico, Histórico, Familiares)
- Mostrar período atual destacado
- Timeline visual para histórico de igrejas
- Cards para familiares

### 2. Validações Visuais
- Mostrar erros de forma clara
- Validar datas em tempo real
- Preview de contrato antes de salvar

### 3. Navegação
- Link "Ver Detalhes" na listagem de pastores
- Breadcrumbs para navegação
- Botões de ação contextuais

## Notas Adicionais

- Manter compatibilidade com código existente (relacionamento Church.shepherd)
- Considerar migração de dados existentes para histórico
- Documentar novo comportamento na documentação do projeto
- Considerar permissões (apenas admin pode gerenciar histórico?)

## Referências

- Django FileField: https://docs.djangoproject.com/en/stable/ref/models/fields/#filefield
- Django DateField: https://docs.djangoproject.com/en/stable/ref/models/fields/#datefield
- dateutil.relativedelta: https://dateutil.readthedocs.io/en/stable/relativedelta.html
