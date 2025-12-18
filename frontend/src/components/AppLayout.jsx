import React, { useState } from 'react'
import { Layout, Menu, theme, Dropdown, Avatar, Space, Badge } from 'antd'
import {
  DashboardOutlined,
  CalendarOutlined,
  DollarOutlined,
  FileTextOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  BellOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import './Sidebar.css'

const { Sider, Header, Content, Footer } = Layout

export default function AppLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false)
  const { token } = theme.useToken()
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/principal',
      icon: <DashboardOutlined />,
      label: 'Principal',
      children: [
        { key: '/principal/dashboard', label: 'Dashboard' },
        { key: '/principal/agendamentos', label: 'Agendamentos' },
      ],
    },
    {
      key: '/financeiro',
      icon: <DollarOutlined />,
      label: 'Financeiro',
      children: [
        { key: '/financeiro/contas', label: 'Contas' },
        { key: '/financeiro/transacoes', label: 'Transações' },
        { key: '/financeiro/comissoes', label: 'Comissões' },
      ],
    },
    {
      key: '/controle',
      icon: <FileTextOutlined />,
      label: 'Controle',
      children: [
        { key: '/controle/compras', label: 'Compras' },
        { key: '/controle/relatorios', label: 'Relatórios' },
      ],
    },
    {
      key: '/cadastro',
      icon: <UserOutlined />,
      label: 'Cadastro',
      children: [
        { key: '/cadastro', label: 'Cadastros' },
      ],
    },
    {
      key: '/marketing',
      icon: <CalendarOutlined />,
      label: 'Marketing',
      children: [
        { key: '/marketing', label: 'Marketing' },
      ],
    },
    {
      key: '/configuracoes',
      icon: <SettingOutlined />,
      label: 'Configurações',
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Meu Perfil',
      icon: <UserOutlined />,
    },
    {
      key: 'settings',
      label: 'Configurações',
      icon: <SettingOutlined />,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: 'Sair',
      icon: <LogoutOutlined />,
      onClick: () => {
        localStorage.removeItem('authToken')
        navigate('/login')
      },
    },
  ]

  const handleMenuClick = (e) => {
    navigate(e.key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={240}
        theme="dark"
        style={{
          background: '#001529',
        }}
      >
        <div className="logo" style={{ padding: '16px', textAlign: 'center', color: '#fff' }}>
          <h2>{collapsed ? 'BA' : 'BoraAgendar'}</h2>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['/']}
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: token.colorBgContainer,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: token.boxShadow,
          }}
        >
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <button
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: '18px',
                border: 'none',
                background: 'none',
                cursor: 'pointer',
              }}
            >
              ☰
            </button>
          </div>

          <Space>
            <Badge count={3}>
              <BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} />
            </Badge>
            <Dropdown menu={{ items: userMenuItems }}>
              <Avatar size="large" icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </Space>
        </Header>

        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            background: token.colorBgContainer,
            borderRadius: token.borderRadius,
            minHeight: 'calc(100vh - 134px)',
          }}
        >
          {children}
        </Content>

        <Footer style={{ textAlign: 'center' }}>
          BoraAgendar ©{new Date().getFullYear()} • Desenvolvido com ❤️
        </Footer>
      </Layout>
    </Layout>
  )
}
