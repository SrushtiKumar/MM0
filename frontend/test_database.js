// Quick test to see what tables exist in Supabase
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ldhzvzxmnshpboocnpiv.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkaHp2enhkbXNocGJvb2NucGl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA3MjkwOTIsImV4cCI6MjA0NjMwNTA5Mn0.3m9ve6G5SIptJfxnB3_FnQbZ9hQPQbE7egPWgZauOPo'

const supabase = createClient(supabaseUrl, supabaseAnonKey)

async function checkTables() {
  console.log('Testing database tables...')
  
  // Test projects table
  try {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .limit(1)
    console.log('Projects table:', { data, error })
  } catch (err) {
    console.log('Projects table error:', err)
  }

  // Test activities table
  try {
    const { data, error } = await supabase
      .from('activities')
      .select('*')
      .limit(1)
    console.log('Activities table:', { data, error })
  } catch (err) {
    console.log('Activities table error:', err)
  }

  // Test files table
  try {
    const { data, error } = await supabase
      .from('files')
      .select('*')
      .limit(1)
    console.log('Files table:', { data, error })
  } catch (err) {
    console.log('Files table error:', err)
  }

  // Test profiles table
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .limit(1)
    console.log('Profiles table:', { data, error })
  } catch (err) {
    console.log('Profiles table error:', err)
  }

  // Test complaints table
  try {
    const { data, error } = await supabase
      .from('complaints')
      .select('*')
      .limit(1)
    console.log('Complaints table:', { data, error })
  } catch (err) {
    console.log('Complaints table error:', err)
  }
}

checkTables()