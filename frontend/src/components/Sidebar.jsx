import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
const LINKS = [
  { to:'/dashboard',  e:'🏠', l:'Dashboard',    p:['administrador','funcionario'] },
  { to:'/pdv',        e:'🛒', l:'Venda (Caixa)', p:['administrador','funcionario'] },
  { to:'/products',   e:'📦', l:'Produtos',      p:['administrador','funcionario'] },
  { to:'/quotations', e:'💰', l:'Orçamentos',    p:['administrador','funcionario'] },
  { to:'/invoices',   e:'🧾', l:'Notas Fiscais', p:['administrador','funcionario'] },
  { to:'/reports',    e:'📊', l:'Relatórios',    p:['administrador','funcionario'] },
  { to:'/clients',    e:'👥', l:'Clientes',      p:['administrador','funcionario'] },
  { to:'/users',      e:'👤', l:'Usuários',      p:['administrador'] },
  { to:'/loyalty',    e:'🏆', l:'Fidelidade',    p:['administrador','funcionario'] },
]
export default function Sidebar() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = async () => { await logout(); navigate('/login') }
  const links = LINKS.filter(l => l.p.includes(usuario?.perfil))
  return (
    <aside className="sidebar">
      <div className="brand">🌸 Flor de Dendê</div>
      <nav className="nav">
        {links.map(({ to, e, l }) => (
          <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'active' : ''}>
            {e} {l}
          </NavLink>
        ))}
        <button onClick={handleLogout}>🚪 Sair</button>
      </nav>
    </aside>
  )
}
