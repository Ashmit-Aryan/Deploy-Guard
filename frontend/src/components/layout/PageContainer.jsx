function PageContainer({ children }) {
  return (
    <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
      {children}
    </main>
  );
}

export default PageContainer;