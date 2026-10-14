from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from apps.core.choices import PerfilUsuario

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email: raise ValueError('E-mail obrigatório.')
        email = self.normalize_email(email)
        extra.setdefault('perfil', PerfilUsuario.FUNCIONARIO)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('perfil',       PerfilUsuario.ADMINISTRADOR)
        extra.setdefault('is_staff',     True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active',    True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    email            = models.EmailField(unique=True)
    username         = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nome             = models.CharField(max_length=150)
    telefone         = models.CharField(max_length=20,  null=True, blank=True)
    cpf              = models.CharField(max_length=14,  null=True, blank=True, unique=True)
    data_nascimento  = models.DateField(null=True, blank=True)
    endereco         = models.CharField(max_length=255, null=True, blank=True)
    cidade           = models.CharField(max_length=100, null=True, blank=True)
    estado           = models.CharField(max_length=2,   null=True, blank=True)
    cep              = models.CharField(max_length=9,   null=True, blank=True)
    perfil           = models.CharField(max_length=20,  choices=PerfilUsuario.CHOICES, default=PerfilUsuario.FUNCIONARIO)
    saldo_pontos         = models.IntegerField(default=0)
    total_pontos_ganhos  = models.IntegerField(default=0)
    total_pontos_resgatados = models.IntegerField(default=0)
    total_compras        = models.IntegerField(default=0)
    vouchers_disponiveis = models.IntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    criado_em  = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects        = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        db_table = 'accounts_user'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.get_perfil_display()})'

    def get_perfil_display(self):
        return dict(PerfilUsuario.CHOICES).get(self.perfil, self.perfil)

    @property
    def is_administrador(self): return self.perfil == PerfilUsuario.ADMINISTRADOR

    def creditar_pontos(self, pontos):
        self.saldo_pontos += pontos
        self.total_pontos_ganhos += pontos
        self.save(update_fields=['saldo_pontos','total_pontos_ganhos','atualizado_em'])

    def debitar_pontos(self, pontos):
        from apps.core.exceptions import PontosInsuficientesError
        if self.saldo_pontos < pontos:
            raise PontosInsuficientesError(self.saldo_pontos, pontos)
        self.saldo_pontos -= pontos
        self.total_pontos_resgatados += pontos
        self.save(update_fields=['saldo_pontos','total_pontos_resgatados','atualizado_em'])

    def registrar_compra(self):
        from django.conf import settings
        self.total_compras += 1
        ganhou = False
        limite = getattr(settings, 'COMPRAS_PARA_VOUCHER', 10)
        if self.total_compras % limite == 0:
            self.vouchers_disponiveis += 1
            ganhou = True
        self.save(update_fields=['total_compras','vouchers_disponiveis','atualizado_em'])
        return ganhou

    def usar_voucher(self):
        if self.vouchers_disponiveis <= 0:
            raise ValueError('Nenhum voucher disponível.')
        self.vouchers_disponiveis -= 1
        self.save(update_fields=['vouchers_disponiveis','atualizado_em'])
