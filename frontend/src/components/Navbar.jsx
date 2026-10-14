import { useAuth } from '../context/AuthContext'
export default function Navbar({ title = '' }) {
  const { usuario } = useAuth()
  return (
    <div className="header">
      <div className="title">{title}</div>
      <div className="user-info">{usuario?.nome}</div>
    </div>
  )
}
