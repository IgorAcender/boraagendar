import React, { useState, useEffect } from 'react'
import {
  Row,
  Col,
  Card,
  Statistic,
  Table,
  Space,
  Button,
  Tag,
  Empty,
  Spin,
  message,
} from 'antd'
import {
  DollarOutlined,
  CalendarOutlined,
  UsersOutlined,
  ShoppingOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { financialAPI } from '../services/api'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [accountSummary, setAccountSummary] = useState(null)
  const [transactionSummary, setTransactionSummary] = useState(null)
  const [commissionSummary, setCommissionSummary] = useState(null)
  const [recentTransactions, setRecentTransactions] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [accounts, transactions, commissions] = await Promise.all([
        financialAPI.getAccountSummary(),
        financialAPI.getTransactionSummary(),
        financialAPI.getCommissionSummary(),
      ])

      setAccountSummary(accounts.data)
      setTransactionSummary(transactions.data)
      setCommissionSummary(commissions.data)

      // Buscar transações recentes
      const tx = await financialAPI.getTransactions({ limit: 5 })
      setRecentTransactions(tx.data.results || [])
    } catch (error) {
      message.error('Erro ao carregar dados do dashboard')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />
  }

  return (
    <div style={{ width: '100%' }}>
      <h1>Dashboard Financeiro</h1>

      {/* Estatísticas Principais */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Saldo Total"
              value={accountSummary?.total_balance || 0}
              prefix="R$ "
              valueStyle={{ color: '#52c41a' }}
              suffix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Receita"
              value={transactionSummary?.income || 0}
              prefix="R$ "
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Despesa"
              value={transactionSummary?.expense || 0}
              prefix="R$ "
              valueStyle={{ color: '#ff4d4f' }}
              suffix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Comissões Pendentes"
              value={commissionSummary?.pending_total || 0}
              prefix="R$ "
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Movimento Financeiro" extra={<Button type="primary" size="small">Exportar</Button>}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={[
                  { name: 'Jan', receita: 4000, despesa: 2400 },
                  { name: 'Fev', receita: 3000, despesa: 1398 },
                  { name: 'Mar', receita: 2000, despesa: 9800 },
                  { name: 'Abr', receita: 2780, despesa: 3908 },
                  { name: 'Mai', receita: 1890, despesa: 4800 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="receita" stroke="#52c41a" />
                <Line type="monotone" dataKey="despesa" stroke="#ff4d4f" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Métodos de Pagamento" extra={<Button type="primary" size="small">Detalhar</Button>}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { name: 'PIX', value: 4000 },
                  { name: 'Cartão', value: 3000 },
                  { name: 'Dinheiro', value: 2000 },
                  { name: 'Transferência', value: 2780 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Transações Recentes */}
      <Card title="Transações Recentes" extra={<Button type="primary">Ver Todas</Button>}>
        {recentTransactions.length > 0 ? (
          <Table
            dataSource={recentTransactions}
            columns={[
              {
                title: 'Descrição',
                dataIndex: 'description',
                key: 'description',
              },
              {
                title: 'Tipo',
                dataIndex: 'transaction_type',
                key: 'transaction_type',
                render: (type) => (
                  <Tag color={type === 'income' ? 'green' : 'red'}>
                    {type === 'income' ? 'Receita' : 'Despesa'}
                  </Tag>
                ),
              },
              {
                title: 'Valor',
                dataIndex: 'amount',
                key: 'amount',
                render: (amount) => `R$ ${amount.toFixed(2)}`,
              },
              {
                title: 'Data',
                dataIndex: 'transaction_date',
                key: 'transaction_date',
              },
            ]}
            pagination={false}
            rowKey="id"
          />
        ) : (
          <Empty description="Nenhuma transação encontrada" />
        )}
      </Card>
    </div>
  )
}
