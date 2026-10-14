from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.core.choices import PerfilUsuario

class LoginSerializer(serializers.Serializer):
    login    = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type':'password'})
    def validate(self, data):
        login = data.get('login','').strip()
        pw    = data.get('password','')
        if not login or not pw: raise serializers.ValidationError('Login e senha obrigatórios.')
        user = None
        if '@' in login:
            user = authenticate(username=login, password=pw)
        else:
            try:
                u = User.objects.get(username=login)
                user = authenticate(username=u.email, password=pw)
            except User.DoesNotExist: pass
        if not user: raise serializers.ValidationError('Login ou senha inválidos.')
        if not user.is_active: raise serializers.ValidationError('Usuário inativo.')
        data['user'] = user
        return data
    def get_tokens(self, user):
        r = RefreshToken.for_user(user)
        return {'refresh': str(r), 'access': str(r.access_token)}

class UserListSerializer(serializers.ModelSerializer):
    perfil_display = serializers.SerializerMethodField()
    def get_perfil_display(self, obj): return obj.get_perfil_display()
    class Meta:
        model = User
        fields = ['id','nome','username','email','telefone','cpf','perfil','perfil_display','is_active','criado_em']

class UserDetailSerializer(serializers.ModelSerializer):
    perfil_display = serializers.SerializerMethodField()
    def get_perfil_display(self, obj): return obj.get_perfil_display()
    class Meta:
        model = User
        fields = ['id','nome','username','email','telefone','cpf','data_nascimento',
                  'endereco','cidade','estado','cep','perfil','perfil_display',
                  'is_active','saldo_pontos','total_compras','vouchers_disponiveis','criado_em','atualizado_em']
        read_only_fields = ['saldo_pontos','total_compras','vouchers_disponiveis','criado_em','atualizado_em']

class UserCreateSerializer(serializers.ModelSerializer):
    password        = serializers.CharField(write_only=True, required=True, style={'input_type':'password'})
    confirmar_senha = serializers.CharField(write_only=True, required=True, style={'input_type':'password'})
    class Meta:
        model = User
        fields = ['nome','username','email','password','confirmar_senha','telefone','cpf','perfil','endereco','cidade','estado','cep']
    def validate_email(self, v):
        v = v.lower().strip()
        if User.objects.filter(email=v).exists(): raise serializers.ValidationError('E-mail já cadastrado.')
        return v
    def validate_username(self, v):
        if v and User.objects.filter(username=v).exists(): raise serializers.ValidationError('Nome de usuário já existe.')
        return v
    def validate(self, data):
        if data['password'] != data['confirmar_senha']: raise serializers.ValidationError({'confirmar_senha':'Senhas não coincidem.'})
        validate_password(data['password']); return data
    def create(self, validated_data):
        validated_data.pop('confirmar_senha'); pw = validated_data.pop('password')
        u = User(**validated_data); u.set_password(pw); u.save(); return u

class UserUpdateSerializer(serializers.ModelSerializer):
    password        = serializers.CharField(write_only=True, required=False, style={'input_type':'password'})
    confirmar_senha = serializers.CharField(write_only=True, required=False, style={'input_type':'password'})
    class Meta:
        model = User
        fields = ['nome','username','email','password','confirmar_senha','telefone','cpf','perfil','endereco','cidade','estado','cep','is_active']
    def validate_username(self, v):
        if v and User.objects.filter(username=v).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Nome de usuário já existe.')
        return v
    def validate(self, data):
        pw = data.get('password'); cp = data.get('confirmar_senha')
        if pw or cp:
            if pw != cp: raise serializers.ValidationError({'confirmar_senha':'Senhas não coincidem.'})
            validate_password(pw)
        return data
    def update(self, instance, validated_data):
        pw = validated_data.pop('password', None); validated_data.pop('confirmar_senha', None)
        for k, v in validated_data.items(): setattr(instance, k, v)
        if pw: instance.set_password(pw)
        instance.save(); return instance

class ClienteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','nome','username','email','telefone','cpf','cidade',
                  'saldo_pontos','total_compras','vouchers_disponiveis','total_pontos_ganhos','is_active']

class ClienteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','nome','username','email','telefone','cpf','data_nascimento',
                  'endereco','cidade','estado','cep',
                  'saldo_pontos','total_pontos_ganhos','total_pontos_resgatados',
                  'total_compras','vouchers_disponiveis','is_active','criado_em','atualizado_em']
        read_only_fields = ['saldo_pontos','total_pontos_ganhos','total_pontos_resgatados',
                            'total_compras','vouchers_disponiveis','criado_em','atualizado_em']

class ClienteCreateSerializer(serializers.ModelSerializer):
    password        = serializers.CharField(write_only=True, required=True, style={'input_type':'password'})
    confirmar_senha = serializers.CharField(write_only=True, required=True, style={'input_type':'password'})
    class Meta:
        model = User
        fields = ['nome','username','email','password','confirmar_senha','telefone','cpf','data_nascimento','endereco','cidade','estado','cep']
    def validate_email(self, v):
        v = v.lower().strip()
        if User.objects.filter(email=v).exists(): raise serializers.ValidationError('E-mail já cadastrado.')
        return v
    def validate_username(self, v):
        if v and User.objects.filter(username=v).exists(): raise serializers.ValidationError('Nome de usuário já existe.')
        return v
    def validate(self, data):
        if data['password'] != data['confirmar_senha']: raise serializers.ValidationError({'confirmar_senha':'Senhas não coincidem.'})
        validate_password(data['password']); return data
    def create(self, validated_data):
        validated_data.pop('confirmar_senha'); pw = validated_data.pop('password')
        u = User(**validated_data, perfil=PerfilUsuario.CLIENTE); u.set_password(pw); u.save(); return u

class ClienteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nome','username','telefone','cpf','data_nascimento','endereco','cidade','estado','cep','is_active']
    def validate_username(self, v):
        if v and User.objects.filter(username=v).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Nome de usuário já existe.')
        return v
