import React, { useState, useEffect } from 'react'
import {
  Table,
  Card,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Popconfirm,
  Tag,
  Empty,
  Spin,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { financialAPI } from '../services/api'

export default function Transactions() {
  const [loading, setLoading] = useState(false)
  const [transactions, setTransactions] = useState([])
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadTransactions()
  }, [])

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const response = await financialAPI.getTransactions()
      setTransactions(response.data.results || response.data || [])
    } catch (error) {
      message.error('Erro ao carregar transações')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingId(null)
    form.resetFields()
    setIsModalVisible(true)
  }

  const handleEdit = (record) => {
    setEditingId(record.id)
    form.setFieldsValue(record)
    setIsModalVisible(true)
  }

  const handleDelete = async (id) => {
    try {
      await financialAPI.deleteTransaction(id)
      message.success('Transação deletada')
      loadTransactions()
    } catch (error) {
      message.error('Erro ao deletar transação')
    }
  }

  const handleSubmit = async (values) => {
    try {
      if (editingId) {
        await financialAPI.updateTransaction(editingId, values)
        message.success('Transação atualizada')
      } else {
        await financialAPI.createTransaction(values)
        message.success('Transação criada')
      }
      setIsModalVisible(false)
      loadTransactions()
    } catch (error) {
      message.error('Erro ao salvar transação')
    }
  }

  const columns = [
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
        <Tag color={type === 'income' ? 'green' : type === 'expense' ? 'red' : 'blue'}>
          {type === 'income' ? 'Receita' : type === 'expense' ? 'Despesa' : 'Transferência'}
        </Tag>
      ),
    },
    {
      title: 'Método',
      dataIndex: 'payment_method',
      key: 'payment_method',
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
    {
      title: 'Ações',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Editar
          </Button>
          <Popconfirm
            title="Confirmar exclusão"
            description="Tem certeza que deseja deletar?"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="danger" size="small" icon={<DeleteOutlined />}>
              Deletar
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="Transações Financeiras"
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
        Nova Transação
      </Button>}
    >
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={transactions}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Spin>

      <Modal
        title={editingId ? 'Editar Transação' : 'Nova Transação'}
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="description"
            label="Descrição"
            rules={[{ required: true, message: 'Descrição é obrigatória' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="transaction_type"
            label="Tipo"
            rules={[{ required: true, message: 'Tipo é obrigatório' }]}
          >
            <Select
              options={[
                { label: 'Receita', value: 'income' },
                { label: 'Despesa', value: 'expense' },
                { label: 'Transferência', value: 'transfer' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="payment_method"
            label="Método de Pagamento"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { label: 'Dinheiro', value: 'cash' },
                { label: 'Cartão Crédito', value: 'card_credit' },
                { label: 'Cartão Débito', value: 'card_debit' },
                { label: 'PIX', value: 'pix' },
                { label: 'Transferência Bancária', value: 'bank_transfer' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="amount"
            label="Valor"
            rules={[{ required: true, message: 'Valor é obrigatório' }]}
          >
            <InputNumber min={0} step={0.01} precision={2} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
